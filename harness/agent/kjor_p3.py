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

Stier: NTB_UT (logger, bygg, kjøringer). NTB_DISK: stien til disken som måles før hvert bygg (standard /). NTB_TRIM (valgfri): kommando som kjøres etter opprydding, slik at en virtuell
maskin gir frigjort diskplass tilbake før diskporten måler (Colima: «colima ssh -- sudo fstrim -a»). Kjøringsfilene for analysen er NTB_UT/p3_kjoringer.jsonl (én linje per forsøk,
med pass, nummer, oppgave, tekstvariant, arm, forsøk, status og kjøringsfeltene fra kjor_agent.py) og NTB_UT/p3_pass.jsonl. Oppgavene leses fra data/sett_v1.jsonl og patchene fra data/instances.jsonl.
"""
import argparse
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


def neste_pass(B, brukt, fullførte):
    """Hva neste pass skal være: 'fullt', 'utvidet' eller None (stopp).
    fullførte: liste med {'kost': samlet kostnad, 'kost_utvidet': kostnad for kjøringene med utvidet tekst, 'type': ...}."""
    if len(fullførte) >= MAKS_PASS:
        return None
    igjen = B - brukt
    if not fullførte:
        return "fullt" if B >= FØRSTE_PASS_MIN else None
    fulle = [p for p in fullførte if p.get("type", "fullt") == "fullt"]
    if fulle and igjen >= MARGIN * max(p["kost"] for p in fulle):
        return "fullt"
    utv = [p["kost_utvidet"] for p in fullførte]
    if utv and igjen >= MARGIN * max(utv):
        return "utvidet"
    return None


def kan_starte_kjøring(B, brukt, arm):
    return brukt + TAK_USD[arm] <= B


def infrastrukturfeil(rad):
    """NTB-0014: Claude Code avslutter med API-feil, eller containeren stopper uten resultatlinje og uten at et tak
    slo inn. `rad` er kjøringsfila fra kjor_agent.kjør()."""
    if rad is None:
        return True
    tak = bool(rad.get("budsjettak_slo_inn")) or bool(rad.get("tidstak_slo_inn"))
    if rad.get("subtype") is None and not tak:
        return True  # ingen resultatlinje
    if rad.get("is_error") and not tak:
        tekst = json.dumps(rad.get("resultat_tekst") or "") + str(rad.get("subtype"))
        if "api" in tekst.lower() or rad.get("subtype") in ("error_during_execution",):
            return True
    return False


def pass_fullført(planlagte, utfall):
    """Fullført når hver planlagt kjøring er gjennomført eller står som manglende. utfall: {nøkkel: status}."""
    return all(utfall.get(k) in ("gjennomfort", "manglende") for k in planlagte)


def sperre(rot=ROT):
    if not (pathlib.Path(rot) / "PREREG_DOI.txt").is_file():
        raise Sperre("PREREG_DOI.txt finnes ikke: ingen agentkjøringer på oppgaver i settet før registrering (NTB-0014)")


# ---------- oppgavefiler ----------

def jl(p):
    return [json.loads(l) for l in pathlib.Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def kort_id(r):
    return f"{r['org']}__{r['repo'].split('/')[1]}__{r['pr']}"


def forbered_oppgaver(ut):
    """Skriver oppgavefiler for begge tekstvarianter, patcher og testlister for kjor_agent.py."""
    sett = jl(ROT / "data/sett_v1.jsonl")
    inst = {r["id"]: r for r in jl(ROT / "data/instances.jsonl")}
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
    f = ledig_gib()
    if f < MIN_DISK_GIB:
        rydd_egne(); f = ledig_gib()
        if f < MIN_DISK_GIB:
            raise RuntimeError(f"under {MIN_DISK_GIB} GiB ledig etter opprydding ({f:.1f} GiB)")
    return round(f, 1)


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
    steg["ledig_gib_for_bygg"] = diskport()
    if not trinn("instansbygg", lambda: (k.bygg_instans(oid)[0], None)):
        return False, steg
    steg["ledig_gib_for_agentbygg"] = diskport()
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
        rad = {"oppgave": oid, "bestatt": ok, "steg": steg, "sekunder_totalt": round(time.time() - t0, 1)}
        rader.append(rad)
        print(json.dumps({"oppgave": oid, "bestatt": ok, "sekunder": rad["sekunder_totalt"],
                          **{s: v.get("ok") for s, v in steg.items() if isinstance(v, dict)}}, ensure_ascii=False), flush=True)
        with open(ut_fil, "a", encoding="utf-8") as f:
            f.write(json.dumps(rad, ensure_ascii=False) + "\n")
    return rader


def kjør_p3(saldo, ut):
    sperre()
    ider = forbered_oppgaver(ut)
    B = budsjett(saldo)
    logg = ut / "p3_logg.jsonl"
    brukt, fullførte = 0.0, []
    k_pr = ka(ut, "pr_tekst")
    k_pr.nett()
    for p in range(1, MAKS_PASS + 1):
        type_ = neste_pass(B, brukt, fullførte)
        if type_ is None:
            break
        varianter = VARIANTER if type_ == "fullt" else ("utvidet",)
        kjøringer = plan(ider, (p,), varianter)
        utfall, kost, kost_utv, stoppet = {}, 0.0, 0.0, False
        for oid in [x for x in oppgaverekkefølge(ider, p)[0]]:
            mine = [x for x in kjøringer if x["oppgave"] == oid]
            if not mine:
                continue
            ok, steg = forberedelse(k_pr, oid, False)
            _skriv(logg, {"pass": p, "oppgave": oid, "forberedelse": steg, "ok": ok})
            if not ok:
                for x in mine:
                    utfall[(x["nummer"])] = "manglende"
                    _skriv(logg, {**x, "status": "manglende", "grunn": "forberedelse feilet"})
                    _skriv(ut / "p3_kjoringer.jsonl", {**x, "status": "manglende", "grunn": "forberedelse feilet"})
                slett_bilder(k_pr, oid); continue
            for x in mine:
                if not kan_starte_kjøring(B, brukt, x["arm"]):
                    stoppet = True; break
                k = ka(ut, x["tekstvariant"])
                for forsøk in range(1, OMKJØRINGER + 2):
                    try:
                        rad = k.kjør(oid, x["arm"], f"{TAK_USD[x['arm']]:.2f}")
                    except SystemExit:
                        raise
                    except Exception as e:  # noqa: BLE001
                        rad = None; _skriv(logg, {**x, "forsok": forsøk, "feil": f"{type(e).__name__}: {str(e)[:200]}"})
                    c = (rad or {}).get("total_cost_usd") or 0.0
                    brukt += c; kost += c
                    if x["tekstvariant"] == "utvidet":
                        kost_utv += c
                    _skriv(ut / "p3_kjoringer.jsonl", {**x, "forsok": forsøk, "status": "forkastet" if infrastrukturfeil(rad) else "gjennomfort",
                                                       **{k2: v for k2, v in (rad or {}).items() if k2 not in x}})
                    if not infrastrukturfeil(rad):
                        utfall[x["nummer"]] = "gjennomfort"
                        _skriv(logg, {**x, "forsok": forsøk, "status": "gjennomfort", "kjoring": rad["kjoring"], "kost": c, "loest": rad["loest"]})
                        break
                    _skriv(logg, {**x, "forsok": forsøk, "status": "forkastet", "kjoring": (rad or {}).get("kjoring"), "kost": c})
                else:
                    utfall[x["nummer"]] = "manglende"
                    _skriv(logg, {**x, "status": "manglende", "grunn": "infrastrukturfeil tre ganger"})
                    _skriv(ut / "p3_kjoringer.jsonl", {**x, "status": "manglende", "grunn": "infrastrukturfeil tre ganger"})
            slett_bilder(k_pr, oid)
            if stoppet:
                break
        fullført = not stoppet and pass_fullført([x["nummer"] for x in kjøringer], utfall)
        _skriv(ut / "p3_pass.jsonl", {"pass": p, "type": type_, "fullfort": fullført, "kost": round(kost, 6), "kost_utvidet": round(kost_utv, 6)})
        _skriv(logg, {"pass": p, "type": type_, "fullfort": fullført, "kost": round(kost, 6), "kost_utvidet": round(kost_utv, 6), "brukt": round(brukt, 6), "B": B})
        if not fullført:
            break
        fullførte.append({"kost": kost, "kost_utvidet": kost_utv, "type": type_})


def _skriv(fil, rad):
    with open(fil, "a", encoding="utf-8") as f:
        f.write(json.dumps({"tid_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **rad}, ensure_ascii=False) + "\n")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("modus", choices=["plan", "kontroll", "kjor"])
    a.add_argument("oppgaver", nargs="*")
    a.add_argument("--ut", default=None)
    a.add_argument("--saldo", type=float, default=None)
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
    else:
        if o.saldo is None:
            raise SystemExit("--saldo mangler (Anthropic-saldo avlest rett før P3)")
        kjør_p3(o.saldo, ut)


if __name__ == "__main__":
    main()
