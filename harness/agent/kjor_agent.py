#!/usr/bin/env python3
"""Kjører Claude Code som agent på én oppgave (NTB-0006, NTB-0007) og vurderer patchen.

Underkommandoer (alle tar oppgave-ID <org>__<repo>__<pr>):
  nett                          opprett det interne nettet ntb-agent og start mellomtjeneren
  bygg <id>                     bygg agentbildet
  selvtest <id> [--modell]      selvtest uten modellkall; med --modell også de to modellkallene (B3)
  kontroll <id>                 vurderingsveien uten modellkall: gullpatch utenom test gir løst, tom patch gir ikke løst
  kjor <id> <modell> <usd>      én agentkjøring med budsjettgrense, deretter vurdering i fersk container uten nett

Stier settes med miljøvariabler (se BRUK.md): NTB_OPPGAVER (mappe med <id>.json: org, repo, pr, basis_sha, url, tittel,
beskrivelse), NTB_PATCHER (<id>/{test,fix}.patch), NTB_TESTER (<id>.json med f2p og p2p), NTB_UT (logger, transkripter,
resultater). Mellomtjeneren får nøkkelen fra miljøvariabelen ANTHROPIC_API_KEY_NORDVAULT i prosessen som starter den
(docker run -e NTB_UPSTREAM_KEY uten verdi); nøkkelen skrives aldri ut.
"""
import base64
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import types

HER = pathlib.Path(__file__).resolve().parent
MSB = pathlib.Path(os.environ.get("NTB_MSB_REPOS", HER.parent / "msb_repos"))
sys.path.insert(0, str(MSB)); sys.path.insert(0, str(HER))
sys.modules["multi_swe_bench.harness.repos"] = types.ModuleType("multi_swe_bench.harness.repos")
import _felles  # noqa: E402
import agentbilde  # noqa: E402
import gullcache  # noqa: E402
import takregel  # noqa: E402
from multi_swe_bench.harness.image import Config  # noqa: E402
from multi_swe_bench.harness.pull_request import Base, PullRequest  # noqa: E402

OPPG = pathlib.Path(os.environ.get("NTB_OPPGAVER", "oppgaver"))
PATCHER = pathlib.Path(os.environ.get("NTB_PATCHER", "patcher"))
TESTER = pathlib.Path(os.environ.get("NTB_TESTER", "tester"))
UT = pathlib.Path(os.environ.get("NTB_UT", "ntb-ut"))
NETT, MT = "ntb-agent", "ntb-mellomtjener"
MT_BILDE = "node@sha256:9d266751ca3d7fdbe651c878ffd5ad0a42fed49a18c283509267c97f025b7496"  # node:24 (har python3)
TIDSGRENSE = 40 * 60  # tidstaket for agenten (NTB-0014)
VURDER_TIDSGRENSE = 40 * 60  # tidsgrense for bygg og vurdering, holdt utenfor agentens tidstak
MT_IMAGE = "nortrebenk-p2/mellomtjener:1"
INNPAKNING = (HER / "innpakning.txt").read_text(encoding="utf-8")


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def oppgave(oid):
    o = json.loads((OPPG / f"{oid}.json").read_text())
    spec = importlib.util.spec_from_file_location(f"ntb_ag_{oid}".replace("-", "_"), MSB / o["org"] / f"{o['repo']}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return o, m


def agentbilde_navn(oid):
    return f"nortrebenk-p2/agent:{oid.lower()}"


def nett():
    if sh(["docker", "network", "inspect", NETT, "--format", "{{.Internal}}"]).stdout.strip() != "true":
        r = sh(["docker", "network", "create", "--internal", "--label", "nortrebenk=p2", NETT])
        if r.returncode:
            raise SystemExit(r.stderr)
    if sh(["docker", "ps", "-q", "--filter", f"name=^{MT}$"]).stdout.strip():
        print("mellomtjener kjører"); return
    sh(["docker", "rm", "-f", MT])
    mappe = UT / "mellomtjener_bygg"; mappe.mkdir(parents=True, exist_ok=True)
    (mappe / "mellomtjener.py").write_text((HER / "mellomtjener.py").read_text())
    (mappe / "Dockerfile").write_text(f"FROM {MT_BILDE}\nLABEL nortrebenk=p2\nCOPY mellomtjener.py /app/mellomtjener.py\n"
                                      "CMD [\"python3\", \"/app/mellomtjener.py\"]\n")
    r = sh(["docker", "build", "--label", "nortrebenk=p2", "-t", MT_IMAGE, str(mappe)])
    if r.returncode:
        raise SystemExit(r.stderr[-500:])
    miljø = {**os.environ, "NTB_UPSTREAM_KEY": os.environ["ANTHROPIC_API_KEY_NORDVAULT"]}
    r = sh(["docker", "run", "-d", "--name", MT, "--label", "nortrebenk=p2", "--network", "bridge",
            "-e", "NTB_UPSTREAM_KEY", MT_IMAGE], env=miljø)
    if r.returncode:
        raise SystemExit("mellomtjeneren startet ikke: " + r.stderr[:300].replace(os.environ["ANTHROPIC_API_KEY_NORDVAULT"], "***"))
    r = sh(["docker", "network", "connect", "--alias", MT, NETT, MT])
    if r.returncode:
        raise SystemExit(r.stderr)
    print("nett og mellomtjener klar")


def bygg(oid):
    o, m = oppgave(oid)
    pr = PullRequest(org=o["org"], repo=o["repo"], number=o["pr"], state="closed", title="", body=None,
                     base=Base(label="", ref="", sha=o["basis_sha"]), resolved_issues=[], fix_patch="", test_patch="")
    mappe = UT / "agentbygg" / oid; mappe.mkdir(parents=True, exist_ok=True)
    (mappe / "Dockerfile").write_text(agentbilde.agent_dockerfile(o["org"], o["repo"], o["basis_sha"], m.Spes, pr=pr, bygg=o.get("bygg")))
    (mappe / "forbered.sh").write_text(agentbilde.forbered(o["repo"], m.Spes, pr))
    if o.get("bygg"):  # gullpatch og testpatch bare for byggesteget «gull» (gullcache.py)
        g = mappe / gullcache.GULL_KATALOG; g.mkdir(exist_ok=True)
        (g / "fix.patch").write_text((PATCHER / oid / "fix.patch").read_text())
        (g / "test.patch").write_text((PATCHER / oid / "test.patch").read_text())
    logg = UT / "logs" / oid; logg.mkdir(parents=True, exist_ok=True)
    with open(logg / "agentbygg.log", "w") as lf:
        r = subprocess.run(["docker", "build", "--label", "nortrebenk=p2", "-t", agentbilde_navn(oid), str(mappe)],
                           stdout=lf, stderr=subprocess.STDOUT, timeout=VURDER_TIDSGRENSE)
    print("agentbilde", "bygget" if r.returncode == 0 else "FEILET", agentbilde_navn(oid))
    return r.returncode == 0


def gull_linjer(oid, n=3):
    fp = (PATCHER / oid / "fix.patch").read_text()
    linjer = [l[1:].strip() for l in fp.splitlines() if l.startswith("+") and not l.startswith("+++")]
    return sorted({l for l in linjer if len(l) >= 30}, key=len, reverse=True)[:n]


def selvtest(oid, modell=False):
    o, _ = oppgave(oid)
    skript = (HER / "selvtest.sh").read_text()
    args = [base64.b64encode(l.encode()).decode() for l in gull_linjer(oid, 10)]  # selvtest.sh velger tre som ikke står på base
    r = sh(["docker", "run", "--rm", "--user", "root", "--network", NETT, "--label", "nortrebenk=p2",
            agentbilde_navn(oid), "bash", "-c", skript, "selvtest", o["repo"], *args], timeout=1800)
    ut = r.stdout.strip()
    res = {"linjer": ut.splitlines(), "bestatt": ut.endswith("SELVTEST BESTATT"), "gull_linjer_sjekket": len(args)}
    if modell:
        start = len(mt_logg())
        r1 = sh(["docker", "run", "--rm", "--network", NETT, "--label", "nortrebenk=p2", agentbilde_navn(oid),
                 "claude", "-p", "Reply with the single word OK.", "--model", "claude-sonnet-5-5", "--output-format", "json"], timeout=600)
        try:
            j = json.loads(r1.stdout); k1 = {"svar": j.get("result"), "total_cost_usd": j.get("total_cost_usd"), "is_error": j.get("is_error")}
        except Exception:  # noqa: BLE001
            k1 = {"feil": (r1.stdout + r1.stderr)[-400:]}
        res["modellkall"] = k1
        res["modellkall_ok"] = bool(k1.get("total_cost_usd")) and not k1.get("is_error")
        r2 = sh(["docker", "run", "--rm", "--network", NETT, "--label", "nortrebenk=p2", agentbilde_navn(oid),
                 "claude", "-p", "Use web search to find the latest released version of the npm package left-pad and give the URL "
                 "of the page you found it on. If you cannot search the web, say so.", "--model", "claude-sonnet-5-5",
                 "--output-format", "json", "--dangerously-skip-permissions"], timeout=900)
        try:
            j = json.loads(r2.stdout); svar = j.get("result") or ""; kost = j.get("total_cost_usd")
        except Exception:  # noqa: BLE001
            svar, kost = (r2.stdout + r2.stderr)[-400:], None
        nye = mt_logg()[start:]
        avvist_web = [l for l in nye if "\tja: web_" in l]
        res["nettsok"] = {"svar": svar[:600], "total_cost_usd": kost, "mellomtjener_linjer": len(nye),
                          "avvist_nettverktoy": len(avvist_web), "url_i_svar": bool(re.search(r"https?://", svar))}
        # Bestått når agenten ikke fikk nettresultater: mellomtjeneren viser enten ingen kall med nettverktøy eller at de
        # ble avvist, og ingen kall med nettverktøy fikk 200. (Første versjon krevde at svaret ikke hadde noen URL; det
        # slo feil når modellen oppga en URL fra hukommelsen. Rettet 16.11.2026.)
        web_ok = [l for l in nye if "web_" in l and "\t200\t" in l]
        res["nettsok_ok"] = not web_ok
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return res


class Selvtestfeil(Exception):
    """Selvtesten rett før en agentkjøring feilet; ingen modellkall er gjort."""


def mt_logg():
    """Mellomtjenerens logg (tid, metode, sti, status, avvist), lest fra containeren og speilet til NTB_UT."""
    r = sh(["docker", "exec", MT, "cat", "/logg/mellomtjener.log"])
    linjer = r.stdout.splitlines() if r.returncode == 0 else []
    (UT / "mellomtjener").mkdir(parents=True, exist_ok=True)
    (UT / "mellomtjener" / "mellomtjener.log").write_text("\n".join(linjer) + ("\n" if linjer else ""))
    return linjer


def instansbilde(o, m, testpatch, fixpatch):
    pr = PullRequest(org=o["org"], repo=o["repo"], number=o["pr"], state="closed", title="", body=None,
                     base=Base(label="", ref="", sha=o["basis_sha"]), resolved_issues=[], fix_patch=fixpatch, test_patch=testpatch)
    return pr, m.Instans(pr, Config(need_clone=True, global_env=None, clear_env=False))


def vurder(oid, agentpatch, navn):
    """Base + agentpatch + testpatch i fersk container fra instansbildet, uten nett. Løst = alle f2p og p2p PASS."""
    o, m = oppgave(oid)
    tp = (PATCHER / oid / "test.patch").read_text(); fp = (PATCHER / oid / "fix.patch").read_text()
    pr, inst = instansbilde(o, m, tp, fp)
    bilde = inst.dependency().image_full_name()
    t = json.loads((TESTER / f"{oid}.json").read_text()); f2p, p2p = set(t["f2p"]), set(t["p2p"])
    d = UT / "vurdering" / navn; d.mkdir(parents=True, exist_ok=True)
    (d / "agent.patch").write_text(agentpatch)
    patcher = "/home/test.patch" + (" /tmp/ntb_agent.patch" if agentpatch.strip() else "")
    skript = _felles._skript(m.Spes, pr, patcher, bool(o.get("bygg")))  # oppgaver med bygg: installasjon på nytt, som i P2.4
    c = sh(["docker", "create", "--network", "none", "--label", "nortrebenk=p2", bilde, "bash", "-c", skript]).stdout.strip()
    try:
        sh(["docker", "cp", str((d / "agent.patch").resolve()), f"{c}:/tmp/ntb_agent.patch"])
        r = sh(["docker", "start", "-a", c], timeout=VURDER_TIDSGRENSE)
    finally:
        sh(["docker", "rm", "-f", c])
    (d / "vurdering.log").write_text(r.stdout + r.stderr)
    tr = inst.parse_log(r.stdout)
    løst = all(x in tr.passed_tests for x in f2p | p2p)
    return {"loest": løst, "patch_feilet": "NORTREBENK_PATCH_FEILET" in r.stdout,
            "ikke_pass": sorted(x for x in f2p | p2p if x not in tr.passed_tests)[:30]}


def bygg_instans(oid):
    """Bygger instansbildet (harness/msb_repos/_felles.py) som vurder() bruker; med cacher fra gulltilstanden for
    oppgaver med feltet `bygg`."""
    o, m = oppgave(oid)
    tp = (PATCHER / oid / "test.patch").read_text(); fp = (PATCHER / oid / "fix.patch").read_text()
    pr, inst = instansbilde(o, m, tp, fp)
    img = inst.dependency()
    mappe = UT / "instansbygg" / oid; mappe.mkdir(parents=True, exist_ok=True)
    (mappe / "Dockerfile").write_text(gullcache.instans_dockerfile(img, o["bygg"]) if o.get("bygg") else img.dockerfile())
    for f in img.files():
        (mappe / f.name).write_text(f.content)
    logg = UT / "logs" / oid; logg.mkdir(parents=True, exist_ok=True)
    with open(logg / "instansbygg.log", "w") as lf:
        r = subprocess.run(["docker", "build", "--label", "nortrebenk=p2", "-t", img.image_full_name(), str(mappe)],
                           stdout=lf, stderr=subprocess.STDOUT, timeout=VURDER_TIDSGRENSE)
    return r.returncode == 0, img.image_full_name()


def testfiler(oid):
    return set(re.findall(r"^diff --git a/(\S+)", (PATCHER / oid / "test.patch").read_text(), re.M))


def uten_testfiler(patch, filer):
    biter = re.split(r"(?m)^(?=diff --git )", patch)
    behold = [b for b in biter if b.startswith("diff --git") and re.match(r"diff --git a/(\S+) b/(\S+)", b).group(2) not in filer
              and re.match(r"diff --git a/(\S+)", b).group(1) not in filer]
    return "".join(behold), len([b for b in biter if b.startswith("diff --git")]) - len(behold)


def kontroll(oid):
    fp = (PATCHER / oid / "fix.patch").read_text()
    gull, _ = uten_testfiler(fp, testfiler(oid))
    a = vurder(oid, gull, f"{oid}__kontroll_gull"); b = vurder(oid, "", f"{oid}__kontroll_tom")
    res = {"gull_utenom_test_loest": a["loest"], "tom_patch_loest": b["loest"], "bestatt": a["loest"] and not b["loest"]}
    print(json.dumps(res, ensure_ascii=False)); return res


def kjør(oid, modell, budsjett):
    o, _ = oppgave(oid)
    st = selvtest(oid)
    if not st["bestatt"]:
        raise Selvtestfeil("selvtesten feilet; ingen agentkjøring")
    prompt = INNPAKNING.replace("{sti}", f"/home/{o['repo']}").replace("{tittel}", o["tittel"]).replace("{beskrivelse}", o["beskrivelse"] or "")
    navn = f"{oid}__{modell}__{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    beholder = "ntb-agent-" + re.sub(r"[^a-zA-Z0-9_.-]", "-", navn)[-60:]
    innpakk = f"""cd /home/{o['repo']}
timeout -k 30 {TIDSGRENSE} claude -p "$NTB_PROMPT" --model {modell} --output-format stream-json --verbose \\
  --dangerously-skip-permissions --disallowedTools WebSearch WebFetch --max-budget-usd {budsjett}
echo $? > /tmp/ntb_exit
git add -A >/dev/null 2>&1
ekskl=$(sed -n 's/^.. //p' /etc/ntb/grunnlinje_status.txt | sed 's/^/:(exclude)/')
git diff --cached --binary HEAD -- . $ekskl > /tmp/ntb_agent.patch
"""
    start_mt = len(mt_logg()); t0 = time.time()
    miljø = {**os.environ, "NTB_PROMPT": prompt}
    try:
        sh(["docker", "run", "--name", beholder, "--network", NETT, "--label", "nortrebenk=p2", "-e", "NTB_PROMPT",
            agentbilde_navn(oid), "bash", "-c", innpakk], env=miljø, timeout=TIDSGRENSE + 600)
    except subprocess.TimeoutExpired:
        sh(["docker", "rm", "-f", beholder])
        raise
    vegg = round(time.time() - t0, 1)
    tdir = UT / "transkripter"; tdir.mkdir(parents=True, exist_ok=True)
    transkript = sh(["docker", "logs", beholder]).stdout
    (tdir / f"{navn}.jsonl").write_text(transkript)
    pdir = UT / "agentpatcher"; pdir.mkdir(parents=True, exist_ok=True)
    sh(["docker", "cp", f"{beholder}:/tmp/ntb_agent.patch", str(pdir / f"{navn}.patch")])
    sh(["docker", "cp", f"{beholder}:/tmp/ntb_exit", str(pdir / f"{navn}.exit")])
    kode = (pdir / f"{navn}.exit").read_text() if (pdir / f"{navn}.exit").exists() else ""
    sh(["docker", "rm", "-f", beholder])
    full = (pdir / f"{navn}.patch").read_text(errors="replace") if (pdir / f"{navn}.patch").exists() else ""
    patch, forkastet = uten_testfiler(full, testfiler(oid))
    resultat = None
    for l in transkript.splitlines():
        try:
            j = json.loads(l)
        except Exception:  # noqa: BLE001
            continue
        if j.get("type") == "result":
            resultat = j
    v = vurder(oid, patch, navn)
    nye = mt_logg()[start_mt:]
    r = resultat or {}
    budsjettak, tidstak = takregel.tak_slo_inn(r.get("subtype"), kode, vegg, TIDSGRENSE)
    kost, kost_satt = takregel.kostnad(r.get("total_cost_usd"), tidstak, budsjett)
    rad = {"kjoring": navn, "oppgave": oid, "url": o["url"], "modell": modell, "budsjett_usd": budsjett,
           "claude_code": agentbilde.CC_VERSJON, "total_cost_usd": kost, "kostnad_satt_til_tak": kost_satt, "usage": r.get("usage"),
           "modelUsage": r.get("modelUsage"), "num_turns": r.get("num_turns"), "duration_ms": r.get("duration_ms"),
           "subtype": r.get("subtype"), "is_error": r.get("is_error"), "resultat_tekst": (r.get("result") or "")[:500], "veggtid_s": vegg,
           "budsjettak_slo_inn": budsjettak, "tidstak_slo_inn": tidstak, "utgangskode": kode.strip(),
           "mellomtjener_kall": len(nye), "mellomtjener_avvist": sum(1 for l in nye if "\tja:" in l),
           "patch_linjer": len(patch.splitlines()), "forkastede_testfilendringer": forkastet,
           "loest_for_takregel": v["loest"], "loest": takregel.loest(v["loest"], budsjettak, tidstak),
           "patch_feilet": v["patch_feilet"], "ikke_pass": v["ikke_pass"],
           "sk_ant_i_transkript": "sk-ant-" in transkript}
    (UT / "kjoringer").mkdir(parents=True, exist_ok=True)
    (UT / "kjoringer" / f"{navn}.json").write_text(json.dumps(rad, ensure_ascii=False, indent=1))
    print(json.dumps({k: rad[k] for k in ("kjoring", "total_cost_usd", "num_turns", "veggtid_s", "loest", "budsjettak_slo_inn",
                                         "tidstak_slo_inn", "mellomtjener_avvist", "sk_ant_i_transkript")}, ensure_ascii=False))
    if rad["sk_ant_i_transkript"]:
        raise SystemExit("STOPP: sk-ant- funnet i transkript")
    return rad


if __name__ == "__main__":
    k = sys.argv[1]
    if k == "nett":
        nett()
    elif k == "bygg":
        sys.exit(0 if bygg(sys.argv[2]) else 1)
    elif k == "selvtest":
        selvtest(sys.argv[2], "--modell" in sys.argv)
    elif k == "kontroll":
        kontroll(sys.argv[2])
    elif k == "kjor":
        kjør(sys.argv[2], sys.argv[3], sys.argv[4])
