#!/usr/bin/env python3
"""P2.2: forseglede instansbilder og stabilitetskjøringer for de P1-validerte oppgavene i ett repo.

Per oppgave: bygg forseglet bilde (p2/msb_repos), kontroller forseglingen, kjør B (testpatch) én gang og C
(testpatch + gullpatch) tre ganger. Første C kjøres med --network none; feiler den på grunn av nett, kjøres alle
tre C med nett (trenger_nett_i_test). «Løst» = alle tester i P1-listene f2p og p2p har PASS.

    python harness/scripts/p22_kjor.py navikt/mock-oauth2-server   # se BRUK.md
"""
import concurrent.futures as cf
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import time
import types

sys.modules["multi_swe_bench.harness.repos"] = types.ModuleType("multi_swe_bench.harness.repos")
import docker  # noqa: E402
from multi_swe_bench.harness.image import Config  # noqa: E402
from multi_swe_bench.harness.pull_request import Base, PullRequest  # noqa: E402

import os  # noqa: E402
HARNESS = pathlib.Path(__file__).resolve().parents[1]
P1 = pathlib.Path(os.environ["NTB_P1"])  # results.jsonl, c2_patcher.jsonl og tester/, se BRUK.md
PATCHER = pathlib.Path(os.environ["NTB_PATCHER"])  # <org>__<repo>__<pr>/{test,fix}.patch
V2 = pathlib.Path(os.environ.get("NTB_UT", "ntb-ut"))  # logger, byggmapper og resultater
sys.path.insert(0, str(HARNESS / "msb_repos"))
MAKS = 40 * 60
NETTFEIL = re.compile(r"UnknownHostException|Could not resolve|Temporary failure in name resolution|ENOTFOUND|EAI_AGAIN|"
                      r"Network is unreachable|Could not GET|Could not HEAD|Failed to download|unable to access|getaddrinfo|"
                      r"Name or service not known|ERR_PNPM_META_FETCH|Could not transfer artifact|Connection refused|"
                      r"NuGet\.Protocol|Unable to load the service index|network is unreachable", re.I)
DISKFEIL = re.compile(r"no space left on device", re.I)


def last(org, repo):
    spec = importlib.util.spec_from_file_location(f"ntb2_{org}_{repo}".replace("-", "_"), HARNESS / "msb_repos" / org / f"{repo}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def bygg(img, mappe, logg, maks):
    mappe.mkdir(parents=True, exist_ok=True)
    (mappe / "Dockerfile").write_text(img.dockerfile(), encoding="utf-8")
    for f in img.files():
        (mappe / f.name).write_text(f.content, encoding="utf-8")
    t0 = time.time()
    try:
        with open(logg, "w") as lf:
            r = subprocess.run(["docker", "build", "--label", "nortrebenk=p2", "-t", img.image_full_name(), str(mappe)],
                               stdout=lf, stderr=subprocess.STDOUT, timeout=maks)
        return ("ok" if r.returncode == 0 else "feil"), time.time() - t0
    except subprocess.TimeoutExpired:
        return "tidsavbrudd", time.time() - t0


def kjør(klient, image, cmd, logg, maks, nett):
    c = klient.containers.run(image, cmd, detach=True, labels={"nortrebenk": "p2"}, network_mode=nett)
    try:
        try:
            c.wait(timeout=maks); tid_ut = False
        except Exception:
            c.kill(); tid_ut = True
        tekst = c.logs().decode("utf-8", "replace")
        pathlib.Path(logg).write_text(tekst, encoding="utf-8")
        return tekst, tid_ut
    finally:
        try:
            c.remove(force=True)
        except Exception:
            pass


def oppgave(klient, mod, rad, cfg, repo_mappe, logrot):
    t0 = time.time(); org, repo = rad["repo"].split("/"); nr = rad["pr"]
    pid = f"{org}__{repo}__{nr}"; ldir = logrot / pid; ldir.mkdir(parents=True, exist_ok=True)
    pdir = PATCHER / pid
    tester = json.loads((P1 / "tester" / f"{pid}.json").read_text())
    f2p, p2p = set(tester["f2p"]), set(tester["p2p"])
    res = {"url": rad["url"], "repo": rad["repo"], "pr": nr, "base_sha": rad["basis_sha"],
           "testpatch_sha256": sha(pdir / "test.patch"), "gullpatch_sha256": sha(pdir / "fix.patch"),
           "patch_gjenskapt": False, "base_image": mod.Spes.base_image, "logsti": str(ldir),
           "disk_omkjoring": False, "forsegling_bryter_bygg": False}
    pr = PullRequest(org=org, repo=repo, number=nr, state="closed", title="", body=None,
                     base=Base(label="", ref="", sha=rad["basis_sha"]), resolved_issues=[],
                     fix_patch=(pdir / "fix.patch").read_text(), test_patch=(pdir / "test.patch").read_text())
    img = mod.Instans(pr, cfg, reinstall=rad.get("deps_reinstall", False)).dependency()
    rest = lambda: MAKS - (time.time() - t0)
    for forsok in (1, 2):
        st, _ = bygg(img, repo_mappe / f"pr-{nr}", ldir / "build.log", max(60, rest()))
        if st == "feil" and DISKFEIL.search((ldir / "build.log").read_text(errors="replace")) and forsok == 1:
            subprocess.run(["docker", "builder", "prune", "-af"], capture_output=True); res["disk_omkjoring"] = True; continue
        break
    if st != "ok":
        res.update(status="bygger_ikke" if st == "feil" else "tidsavbrudd", i_settet_etter_p22="nei",
                   varighet_s=round(time.time() - t0)); return res
    # forsegling
    r = subprocess.run(["docker", "run", "--rm", "--network", "none", img.image_full_name(), "bash", "-c",
                        f"cat /home/forsegling.txt; cd /home/{repo}; git log --all --oneline | wc -l; git remote -v | wc -l; git for-each-ref | wc -l"],
                       capture_output=True, text=True, timeout=300)
    ut = r.stdout.split()
    res["forsegling"] = {"merke": ut[0] if ut else None, "commits_all": ut[1] if len(ut) > 1 else None,
                         "remotes": ut[2] if len(ut) > 2 else None, "refs": ut[3] if len(ut) > 3 else None}
    res["forsegling_kontrollert"] = ut[:4] == ["FORSEGLET", "1", "0", "1"]
    løst = lambda tr: all(t in tr.passed_tests for t in f2p | p2p)
    inst = mod.Instans(pr, cfg)
    # B
    tekst, tid_ut = kjør(klient, img.image_full_name(), inst.test_patch_run(), ldir / "B.log", max(30, rest()), "bridge")
    if tid_ut:
        res.update(status="tidsavbrudd", aarsak="B", i_settet_etter_p22="nei", varighet_s=round(time.time() - t0)); return res
    rB = inst.parse_log(tekst)
    res["loest_B"] = løst(rB)
    res["f2p_fail_i_B"] = sum(1 for t in f2p if t in rB.failed_tests)
    res["f2p_mangler_i_B"] = sum(1 for t in f2p if t not in (rB.passed_tests | rB.failed_tests | rB.skipped_tests))
    res["testpatch_kompilerer_mot_base"] = "ja" if res["f2p_mangler_i_B"] == 0 else ("nei" if res["f2p_mangler_i_B"] == len(f2p) else "delvis")
    # C
    nett = "none"; res["trenger_nett_i_test"] = False; c_res = []
    i = 1
    while i <= 3:
        if rest() <= 30:
            res.update(status="tidsavbrudd", aarsak=f"før C{i}"); break
        tekst, tid_ut = kjør(klient, img.image_full_name(), inst.fix_patch_run(), ldir / f"C{i}_{nett}.log", rest(), nett)
        if tid_ut:
            res.update(status="tidsavbrudd", aarsak=f"C{i}"); break
        if DISKFEIL.search(tekst) and not res.get("_disk_c"):
            res["_disk_c"] = True; res["disk_omkjoring"] = True; continue
        rC = inst.parse_log(tekst)
        if i == 1 and nett == "none" and not løst(rC) and NETTFEIL.search(tekst):
            res["trenger_nett_i_test"] = True; nett = "bridge"; continue
        c_res.append({"loest": løst(rC), "nett": nett,
                      "ikke_pass": sorted(t for t in f2p | p2p if t not in rC.passed_tests)[:50]})
        i += 1
    res.pop("_disk_c", None)
    res["C"] = c_res
    res["loest_C_antall"] = sum(1 for c in c_res if c["loest"])
    if "status" not in res:
        res["status"] = "ferdig"
    res["i_settet_etter_p22"] = "ja" if (res["status"] == "ferdig" and not res["loest_B"] and res["loest_C_antall"] == 3
                                        and len(c_res) == 3 and res["forsegling_kontrollert"]) else "nei"
    res["varighet_s"] = round(time.time() - t0)
    subprocess.run(["docker", "rmi", "-f", img.image_full_name()], capture_output=True)
    return res


def main():
    org, repo = sys.argv[1].split("/"); par = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    mod = last(org, repo)
    p1res = [json.loads(l) for l in open(P1 / "results.jsonl")]
    val = {r["url"] for r in p1res if r["status"] == "validert" and r["repo"] == f"{org}/{repo}"}
    c2 = [json.loads(l) for l in open(P1 / "c2_patcher.jsonl")]
    rader = [r for r in c2 if r["url"] in val]
    cfg = Config(need_clone=True, global_env=None, clear_env=False)
    klient = docker.from_env(timeout=7200)
    repo_mappe = V2 / "work" / org / repo; logrot = V2 / "logs"; logrot.mkdir(parents=True, exist_ok=True)
    ut = V2 / "res"; ut.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with cf.ThreadPoolExecutor(par) as ex:
        fut = {ex.submit(oppgave, klient, mod, r, cfg, repo_mappe, logrot): r for r in rader}
        for f in cf.as_completed(fut):
            r = fut[f]
            try:
                res = f.result()
            except Exception as e:  # noqa: BLE001
                res = {"url": r["url"], "repo": r["repo"], "pr": r["pr"], "status": "kjorefeil",
                       "aarsak": f"{type(e).__name__}: {str(e)[:200]}", "i_settet_etter_p22": "nei"}
            (ut / f"{org}__{repo}__{r['pr']}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
            print(f"{r['pr']}: {res['status']} B={res.get('loest_B')} C={res.get('loest_C_antall')}/3 nett={res.get('trenger_nett_i_test')} "
                  f"forseglet={res.get('forsegling_kontrollert')} kompilerer={res.get('testpatch_kompilerer_mot_base')} sett={res['i_settet_etter_p22']} "
                  f"{res.get('varighet_s')} s {res.get('aarsak', '')}", flush=True)
    print(f"ferdig {org}/{repo} på {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
