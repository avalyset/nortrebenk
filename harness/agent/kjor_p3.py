#!/usr/bin/env python3
"""Kjører P3 etter NTB-0014.

P3 kjøres i inntil tre pass. Ett pass er én kjøring per oppgave, arm og tekstvariant (84 kjøringer for 21 oppgaver).
Innen et pass tas oppgavene i en rekkefølge stokket med frø 20261116 + passnummeret, og hver oppgaves kjøringer i en
rekkefølge gitt av samme frø. For hver oppgave: bygg instansbilde og agentbilde, selvtest, kontroll av
vurderingsveien (gullpatch utenom testfiler gir løst, tom patch gir ikke løst), kjøringene én om gangen, og sletting
av bildene.

Moduser:
  plan [--ut data/p3_plan.jsonl]                 tørrkjøring uten Docker og uten modellkall; skriver planen
  kontroll <id>... [--ut data/p3_kontroll.jsonl]  alt unntatt agentkjøringene, for oppgitte oppgaver
  kjor --saldo <USD>                              P3; nekter å starte før PREREG_DOI.txt finnes i repoet
  prove --sett <fil> --instanser <fil> --saldo <USD>
                                                  samme sløyfe som kjor med bare PR-teksten og ett pass, for oppgaver
                                                  utenfor settet (generalprøve); nekter oppgaver i data/sett_v1.jsonl

Gjenopptak (NTB-0014, endret 17.11.2026): ved første start skrives NTB_UT/p3_start.json med B; senere starter bruker B
derfra. Brukt er summen av total_cost_usd i p3_kjoringer.jsonl. Fullførte pass leses fra p3_pass.jsonl; har den et pass
som ikke er fullført (stoppet av budsjettet), nekter kjøreren å fortsette. I passet som pågår, hoppes kjøringer med
status gjennomfort eller manglende over, og forkastede forsøk teller videre mot grensen på to omkjøringer.

Stier: NTB_UT (logger, bygg, kjøringer). NTB_DISK: stien til disken som måles før hvert bygg (standard /). NTB_TRIM (valgfri): kommando som kjøres etter opprydding, slik at en virtuell
maskin gir frigjort diskplass tilbake før diskporten måler (Colima: «colima ssh -- sudo fstrim -a»). Kjøringsfilene for analysen er NTB_UT/p3_kjoringer.jsonl (én linje per forsøk,
med pass, nummer, oppgave, tekstvariant, arm, forsøk, status og kjøringsfeltene fra kjor_agent.py) og NTB_UT/p3_pass.jsonl. Oppgavene leses fra data/sett_v1.jsonl og patchene fra data/instances.jsonl.
"""
import argparse
import collections
import json
import os
import pathlib
import random
import shutil
import subprocess
import sys
import time

HER = pathlib.Path(__file__).resolve().parent
ROT = HER.parent.parent
FRØ = 20261116
ARMER = ("claude-sonnet-5-5", "claude-opus-5-5")
TAK_USD = {"claude-sonnet-5-5": 1.50, "claude-opus-5-5": 3.00}
VARIANTER = ("pr_tekst", "utvidet")
MAKS_PASS = 3
FØRSTE_PASS_MIN = 28.29  # 1,5 × to runder à 9,43 USD (data/roykprove/budsjett.md, høyeste målte)
RESERVE = 5.00
MARGIN = 1.5
OMKJØRINGER = 2
MIN_DISK_GIB = 6


class Sperre(Exception):
    pass


# ---------- rene regler (testes i tests/) ----------

def oppgaverekkefølge(ider, pass_nr):
    rng = random.Random(FRØ + pass_nr)
    ider = sorted(ider)
    rng.shuffle(ider)
    return ider, rng


def plan(ider, pass_liste=(1, 2, 3), varianter=VARIANTER):
    """Alle kjøringer i rekkefølge: (pass, nummer, oppgave, tekstvariant, arm). Nummer teller innen passet."""
    ut = []
    for p in pass_liste:
        rekke, rng = oppgaverekkefølge(ider, p)
        n = 0
        for oid in rekke:
            komb = [(v, a) for v in VARIANTER for a in ARMER]
            rng.shuffle(komb)
            for v, a in komb:
                if v not in varianter:
                    continue
                n += 1
                ut.append({"pass": p, "nummer": n, "oppgave": oid, "tekstvariant": v, "arm": a})
    return ut


def budsjett(saldo):
    return round(saldo - RESERVE, 6)


def neste_pass(B, brukt, fullførte, maks=MAKS_PASS):
    """Hva neste pass skal være: 'fullt', 'utvidet' eller None (stopp).
    fullførte: liste med {'kost': samlet kostnad, 'kost_utvidet': kostnad for kjøringene med utvidet tekst, 'type': ...}.
    Terskelen for et pass med bare utvidet tekst er 1,5 × utvidet-delen av det fullførte passet med høyest kost."""
    if len(fullførte) >= maks:
        return None
    igjen = B - brukt
    if not fullførte:
        return "fullt" if B >= FØRSTE_PASS_MIN else None
    fulle = [p for p in fullførte if p.get("type", "fullt") == "fullt"]
    if fulle and igjen >= MARGIN * max(p["kost"] for p in fulle):
        return "fullt"
    dyreste = max(fullførte, key=lambda p: p["kost"])
    if igjen >= MARGIN * dyreste["kost_utvidet"]:
        return "utvidet"
    return None


def kan_starte_kjøring(B, brukt, arm):
    return brukt + TAK_USD[arm] <= B


def infrastrukturfeil(rad):
    """NTB-0014: uten at et tak slo inn, avslutter Claude Code med API-feil eller kjøringsfeil (subtype
    error_during_execution, endret 17.11.2026), eller containeren stopper uten resultatlinje. `rad` er kjøringsfila fra
    kjor_agent.kjør()."""
    if rad is None:
        return True
    tak = bool(rad.get("budsjettak_slo_inn")) or bool(rad.get("tidstak_slo_inn"))
    if rad.get("subtype") is None and not tak:
        return True  # ingen resultatlinje
    if rad.get("subtype") == "error_during_execution" and not tak:
        return True
    if rad.get("is_error") and not tak:
        tekst = json.dumps(rad.get("resultat_tekst") or "") + str(rad.get("subtype"))
        if "api" in tekst.lower() or rad.get("subtype") in ("error_during_execution",):
            return True
    return False


def pass_fullført(planlagte, utfall):
    """Fullført når hver planlagt kjøring er gjennomført eller står som manglende. utfall: {nøkkel: status}."""
    return all(utfall.get(k) in ("gjennomfort", "manglende") for k in planlagte)


def nøkkel(x):
    return (x["pass"], x["oppgave"], x["tekstvariant"], x["arm"])


def utfall_fra(rader):
    """{nøkkel: status} for kjøringer med status gjennomfort eller manglende, og {nøkkel: antall forkastede forsøk}."""
    utfall, forkastet = {}, collections.Counter()
    for r in rader:
        if r.get("pass") is None:
            continue
        if r.get("status") in ("gjennomfort", "manglende"):
            utfall[nøkkel(r)] = r["status"]
        elif r.get("status") == "forkastet":
            forkastet[nøkkel(r)] += 1
    return utfall, forkastet


def gjenopptak(rader, pass_rader, ider, B, varianter=VARIANTER, maks=MAKS_PASS):
    """Tilstanden ved start eller omstart (NTB-0014, endret 17.11.2026), fra radene i p3_kjoringer.jsonl og
    p3_pass.jsonl. Nekter (Sperre) hvis et pass i p3_pass.jsonl ikke er fullført. Passet som pågår, er det første som
    ikke står i p3_pass.jsonl; typen avgjøres med det som var brukt før passet, slik den ble ved passets start.
    Returnerer brukt, fullførte pass, passet, typen (None: stopp), alle planlagte kjøringer i passet og de gjenstående."""
    ufull = sorted(p["pass"] for p in pass_rader if not p.get("fullfort"))
    if ufull:
        raise Sperre(f"p3_pass.jsonl har pass som ikke er fullført ({ufull}); kjøreren fortsetter ikke")
    fullførte = [{"pass": p["pass"], "kost": p["kost"], "kost_utvidet": p["kost_utvidet"], "type": p.get("type", "fullt")}
                 for p in sorted(pass_rader, key=lambda p: p["pass"])]
    brukt = sum(r.get("total_cost_usd") or 0.0 for r in rader)
    p = len(fullførte) + 1
    brukt_før = sum(r.get("total_cost_usd") or 0.0 for r in rader if (r.get("pass") or 0) < p)
    type_ = neste_pass(B, brukt_før, fullførte, maks)
    utfall, forkastet = utfall_fra(rader)
    kjøringer = plan(ider, (p,), varianter if type_ == "fullt" else ("utvidet",)) if type_ else []
    return {"brukt": brukt, "fullforte": fullførte, "pass": p, "type": type_, "kjoringer": kjøringer,
            "gjenstaende": [x for x in kjøringer if nøkkel(x) not in utfall], "forkastet": forkastet}


def sperre(rot=ROT):
    if not (pathlib.Path(rot) / "PREREG_DOI.txt").is_file():
        raise Sperre("PREREG_DOI.txt finnes ikke: ingen agentkjøringer på oppgaver i settet før registrering (NTB-0014)")


# ---------- oppgavefiler ----------

def jl(p):
    return [json.loads(l) for l in pathlib.Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def kort_id(r):
    return f"{r['org']}__{r['repo'].split('/')[1]}__{r['pr']}"


def forbered_oppgaver(ut, sett_fil=None, inst_fil=None):
    """Skriver oppgavefiler for begge tekstvarianter, patcher og testlister for kjor_agent.py."""
    sett = jl(sett_fil or ROT / "data/sett_v1.jsonl")
    inst = {r["id"]: r for r in jl(inst_fil or ROT / "data/instances.jsonl")}
    for r in sett:
        oid = kort_id(r); i = inst[r["id"]]
        tittel, beskr = r["pr_tekst"]["tittel"], r["pr_tekst"]["beskrivelse"] or ""
        utv = r["utvidet_tekst"]
        assert utv.startswith(tittel), oid
        felles = {"org": r["org"], "repo": r["repo"].split("/")[1], "pr": r["pr"], "url": r["url"], "basis_sha": r["base_sha"],
                  "tittel": tittel, **({"bygg": r["bygg"]} if r.get("bygg") else {})}
        for v, b in (("pr_tekst", beskr), ("utvidet", utv[len(tittel):].lstrip("\n"))):
            d = ut / "oppgaver" / v; d.mkdir(parents=True, exist_ok=True)
            (d / f"{oid}.json").write_text(json.dumps({**felles, "beskrivelse": b}, ensure_ascii=False, indent=1))
        p = ut / "patcher" / oid; p.mkdir(parents=True, exist_ok=True)
        (p / "fix.patch").write_text(i["gullpatch"]); (p / "test.patch").write_text(i["testpatch"])
        t = ut / "tester"; t.mkdir(parents=True, exist_ok=True)
        (t / f"{oid}.json").write_text(json.dumps({"f2p": r["f2p"], "p2p": r["p2p"]}, ensure_ascii=False))
    return [kort_id(r) for r in sett]


def ka(ut, variant="pr_tekst"):
    """Laster kjor_agent.py med stiene for P3."""
    os.environ.update(NTB_OPPGAVER=str(ut / "oppgaver" / variant), NTB_PATCHER=str(ut / "patcher"),
                      NTB_TESTER=str(ut / "tester"), NTB_UT=str(ut))
    sys.path.insert(0, str(HER))
    import kjor_agent
    kjor_agent.OPPG = ut / "oppgaver" / variant
    return kjor_agent


# ---------- Docker ----------

def ledig_gib(sti=None):
    sti = sti or os.environ.get("NTB_DISK", "/")  # disken Docker-dataene ligger på
    return shutil.disk_usage(sti).free / 2**30


def rydd_egne():
    """Sletter egne images (label nortrebenk=p2) unntatt mellomtjeneren og images oppført i NTB_VERNEDE_IMAGES."""
    ut = subprocess.run(["docker", "images", "-a", "--filter", "label=nortrebenk=p2", "--format", "{{.ID}} {{.Repository}}"],
                        capture_output=True, text=True).stdout.split("\n")
    vern = set()
    vf = os.environ.get("NTB_VERNEDE_IMAGES")
    if vf and os.path.exists(vf):
        vern = {l.strip()[:12] for l in open(vf) if l.strip()}
    mt = {l.split()[0] for l in ut if l.strip().endswith("nortrebenk-p2/mellomtjener")}
    for i in sorted({l.split()[0] for l in ut if l.strip()}):
        if i[:12] not in vern and i not in mt:
            subprocess.run(["docker", "rmi", "-f", i], capture_output=True)
    subprocess.run(["docker", "builder", "prune", "-af"], capture_output=True)
    trim = os.environ.get("NTB_TRIM")  # f.eks. «colima ssh -- sudo fstrim -a»: gir VM-ens frigjorte blokker tilbake til verten
    if trim:
        subprocess.run(trim.split(), capture_output=True)


def diskport():
    """(ok, ledig GiB). Under MIN_DISK_GIB etter opprydding er ikke ok: bygget startes ikke, og oppgavens kjøringer i
    passet står som manglende (NTB-0014, endret 17.11.2026)."""
    f = ledig_gib()
    if f < MIN_DISK_GIB:
        rydd_egne(); f = ledig_gib()
    return f >= MIN_DISK_GIB, round(f, 1)


def forberedelse(k, oid, med_tid):
    """Bygg, selvtest og kontroll for én oppgave, med høyst to forsøk per steg. Returnerer (ok, steg)."""
    steg = {}
    def trinn(navn, f):
        for forsøk in (1, 2):
            t0 = time.time()
            try:
                ok, detalj = f()
            except Exception as e:  # noqa: BLE001
                ok, detalj = False, f"{type(e).__name__}: {str(e)[:200]}"
            steg[navn] = {"ok": ok, "forsok": forsøk, "sekunder": round(time.time() - t0, 1), "detalj": detalj}
            if ok:
                return True
        return False
    ok, steg["ledig_gib_for_bygg"] = diskport()
    if not ok:
        steg["grunn"] = f"under {MIN_DISK_GIB} GiB ledig"; return False, steg
    if not trinn("instansbygg", lambda: (k.bygg_instans(oid)[0], None)):
        return False, steg
    ok, steg["ledig_gib_for_agentbygg"] = diskport()
    if not ok:
        steg["grunn"] = f"under {MIN_DISK_GIB} GiB ledig"; return False, steg
    if not trinn("agentbygg", lambda: (k.bygg(oid), None)):
        return False, steg
    def st():
        r = k.selvtest(oid); return r["bestatt"], r["linjer"]
    if not trinn("selvtest", st):
        return False, steg
    def kt():
        r = k.kontroll(oid); return r["bestatt"], r
    if not trinn("kontroll", kt):
        return False, steg
    return True, steg


def slett_bilder(k, oid):
    o, m = k.oppgave(oid)
    tp = (k.PATCHER / oid / "test.patch").read_text(); fp = (k.PATCHER / oid / "fix.patch").read_text()
    _, inst = k.instansbilde(o, m, tp, fp)
    for navn in (inst.dependency().image_full_name(), k.agentbilde_navn(oid)):
        subprocess.run(["docker", "rmi", "-f", navn], capture_output=True)
    rydd_egne()


def kontroll_modus(ider, ut_fil, ut):
    forbered_oppgaver(ut)
    k = ka(ut)
    rader = []
    for oid in ider:
        t0 = time.time()
        ok, steg = forberedelse(k, oid, True)
        t_slett = time.time()
        slett_bilder(k, oid)
        steg["sletting"] = {"ok": True, "sekunder": round(time.time() - t_slett, 1)}
        rad = {"oppgave": oid, "bestatt": ok, **({"grunn": steg["grunn"]} if "grunn" in steg else {}), "steg": steg,
               "sekunder_totalt": round(time.time() - t0, 1)}
        rader.append(rad)
        print(json.dumps({"oppgave": oid, "bestatt": ok, "sekunder": rad["sekunder_totalt"],
                          **{s: v.get("ok") for s, v in steg.items() if isinstance(v, dict)}}, ensure_ascii=False), flush=True)
        with open(ut_fil, "a", encoding="utf-8") as f:
            f.write(json.dumps(rad, ensure_ascii=False) + "\n")
    return rader


def start_budsjett(ut, saldo):
    """B fra NTB_UT/p3_start.json når den finnes; ellers B = saldo − reserve, skrevet dit ved første start."""
    f = ut / "p3_start.json"
    if f.is_file():
        return json.loads(f.read_text(encoding="utf-8"))["B"]
    if saldo is None:
        raise SystemExit("--saldo mangler (Anthropic-saldo avlest rett før start)")
    B = budsjett(saldo)
    f.write_text(json.dumps({"B": B, "saldo": saldo, "tid_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                            ensure_ascii=False) + "\n", encoding="utf-8")
    return B


def kjør_én(k, ut, oid, x, B, brukt, forkastet_før, logg):
    """Én planlagt kjøring med inntil to omkjøringer. Budsjettsjekk før hvert forsøk. Selvtestfeil rett før
    kjøringen prøves én gang til. Returnerer (utfall, brukt): 'gjennomfort', 'manglende', 'budsjett' eller 'selvtest'."""
    for forsøk in range(forkastet_før + 1, OMKJØRINGER + 2):
        if not kan_starte_kjøring(B, brukt, x["arm"]):
            _skriv(logg, {**x, "forsok": forsøk, "status": "ikke startet", "grunn": "budsjett", "brukt": round(brukt, 6), "B": B})
            return "budsjett", brukt
        rad = None
        for st_forsøk in (1, 2):
            try:
                rad = k.kjør(oid, x["arm"], f"{TAK_USD[x['arm']]:.2f}")
                break
            except k.Selvtestfeil:
                _skriv(logg, {**x, "forsok": forsøk, "selvtest_feilet": st_forsøk})
                if st_forsøk == 2:
                    return "selvtest", brukt
            except SystemExit:
                raise
            except Exception as e:  # noqa: BLE001
                rad = None; _skriv(logg, {**x, "forsok": forsøk, "feil": f"{type(e).__name__}: {str(e)[:200]}"})
                break
        c = (rad or {}).get("total_cost_usd") or 0.0
        brukt += c
        status = "forkastet" if infrastrukturfeil(rad) else "gjennomfort"
        _skriv(ut / "p3_kjoringer.jsonl", {**x, "forsok": forsøk, "status": status, **{k2: v for k2, v in (rad or {}).items() if k2 not in x}})
        _skriv(logg, {**x, "forsok": forsøk, "status": status, "kjoring": (rad or {}).get("kjoring"), "kost": c,
                      **({"loest": rad.get("loest")} if status == "gjennomfort" else {})})
        if status == "gjennomfort":
            return "gjennomfort", brukt
    _manglende(ut, logg, x, "infrastrukturfeil tre ganger")
    return "manglende", brukt


def _manglende(ut, logg, x, grunn):
    _skriv(logg, {**x, "status": "manglende", "grunn": grunn})
    _skriv(ut / "p3_kjoringer.jsonl", {**x, "status": "manglende", "grunn": grunn})


def kjør_løkke(ut, ider, B, varianter=VARIANTER, maks=MAKS_PASS):
    """Passene etter NTB-0014, med gjenopptak fra p3_kjoringer.jsonl og p3_pass.jsonl."""
    logg, kj_fil, pass_fil = ut / "p3_logg.jsonl", ut / "p3_kjoringer.jsonl", ut / "p3_pass.jsonl"
    k_pr = None
    while True:
        st = gjenopptak(jl_om(kj_fil), jl_om(pass_fil), ider, B, varianter, maks)
        if st["type"] is None:
            _skriv(logg, {"hendelse": "ingen flere pass", "fullforte_pass": len(st["fullforte"]), "brukt": round(st["brukt"], 6), "B": B})
            return
        p, brukt = st["pass"], st["brukt"]
        _skriv(logg, {"hendelse": "pass starter", "pass": p, "type": st["type"], "planlagte": len(st["kjoringer"]),
                      "gjenstaende": len(st["gjenstaende"]), "brukt": round(brukt, 6), "B": B})
        if k_pr is None:
            k_pr = ka(ut, "pr_tekst")
            k_pr.nett()
        stoppet = False
        for oid in oppgaverekkefølge(ider, p)[0]:
            mine = [x for x in st["gjenstaende"] if x["oppgave"] == oid]
            if not mine:
                continue  # oppgaver uten gjenstående kjøringer bygges ikke
            ok, steg = forberedelse(k_pr, oid, False)
            _skriv(logg, {"pass": p, "oppgave": oid, "forberedelse": steg, "ok": ok})
            if not ok:
                for x in mine:
                    _manglende(ut, logg, x, steg.get("grunn", "forberedelse feilet"))
                slett_bilder(k_pr, oid); continue
            for i, x in enumerate(mine):
                res, brukt = kjør_én(ka(ut, x["tekstvariant"]), ut, oid, x, B, brukt, st["forkastet"][nøkkel(x)], logg)
                if res == "budsjett":
                    stoppet = True; break
                if res == "selvtest":
                    for y in mine[i:]:
                        _manglende(ut, logg, y, "selvtest feilet før kjøring")
                    break
            slett_bilder(k_pr, oid)
            if stoppet:
                break
        rader_p = [r for r in jl_om(kj_fil) if r.get("pass") == p]
        utfall, _ = utfall_fra(rader_p)
        fullført = not stoppet and pass_fullført([nøkkel(x) for x in st["kjoringer"]], utfall)
        kost = sum(r.get("total_cost_usd") or 0.0 for r in rader_p)
        kost_utv = sum(r.get("total_cost_usd") or 0.0 for r in rader_p if r["tekstvariant"] == "utvidet")
        varianter_p = sorted({x["tekstvariant"] for x in st["kjoringer"]})
        _skriv(pass_fil, {"pass": p, "type": st["type"], "varianter": varianter_p, "fullfort": fullført,
                          "kost": round(kost, 6), "kost_utvidet": round(kost_utv, 6)})
        _skriv(logg, {"pass": p, "type": st["type"], "fullfort": fullført, "kost": round(kost, 6), "kost_utvidet": round(kost_utv, 6),
                      "brukt": round(brukt, 6), "B": B})
        if not fullført:
            return


def kjør_p3(saldo, ut):
    sperre()
    ider = forbered_oppgaver(ut)
    kjør_løkke(ut, ider, start_budsjett(ut, saldo))


def prøve(saldo, ut, sett_fil, inst_fil):
    """Generalprøve: samme sløyfe som kjor, med bare PR-teksten og ett pass, for oppgaver utenfor settet."""
    i_settet = {kort_id(r) for r in jl(ROT / "data/sett_v1.jsonl")}
    treff = sorted({kort_id(r) for r in jl(sett_fil)} & i_settet)
    if treff:
        raise Sperre(f"prove nekter oppgaver i data/sett_v1.jsonl: {treff}")
    ider = forbered_oppgaver(ut, sett_fil, inst_fil)
    kjør_løkke(ut, ider, start_budsjett(ut, saldo), ("pr_tekst",), 1)


def jl_om(p):
    return jl(p) if pathlib.Path(p).is_file() else []


def _skriv(fil, rad):
    with open(fil, "a", encoding="utf-8") as f:
        f.write(json.dumps({"tid_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **rad}, ensure_ascii=False) + "\n")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("modus", choices=["plan", "kontroll", "kjor", "prove"])
    a.add_argument("oppgaver", nargs="*")
    a.add_argument("--ut", default=None)
    a.add_argument("--saldo", type=float, default=None)
    a.add_argument("--sett", default=None)
    a.add_argument("--instanser", default=None)
    o = a.parse_args()
    ut = pathlib.Path(os.environ.get("NTB_UT", "ntb-ut")); ut.mkdir(parents=True, exist_ok=True)
    if o.modus == "plan":
        ider = [kort_id(r) for r in jl(ROT / "data/sett_v1.jsonl")]
        p = plan(ider)
        fil = pathlib.Path(o.ut or ROT / "data/p3_plan.jsonl")
        fil.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in p), encoding="utf-8")
        print(f"{len(p)} kjøringer i planen skrevet til {fil.name}")
    elif o.modus == "kontroll":
        kontroll_modus(o.oppgaver, pathlib.Path(o.ut or ROT / "data/p3_kontroll.jsonl"), ut)
    elif o.modus == "prove":
        if not (o.sett and o.instanser):
            raise SystemExit("prove krever --sett og --instanser")
        prøve(o.saldo, ut, pathlib.Path(o.sett), pathlib.Path(o.instanser))
    else:
        kjør_p3(o.saldo, ut)


if __name__ == "__main__":
    main()
