#!/usr/bin/env python3
"""Analyse av P3 (NTB-0008, NTB-0013, NTB-0014). Beskrivende; ingen hypotesetester.

Leser kjøringsfilene fra P3 (p3_kjoringer.jsonl og p3_pass.jsonl fra harness/agent/kjor_p3.py), data/sett_v1.jsonl og
data/kvalitet/uavhengig_utvidet.jsonl. Kan også lese en kjøringsfil i formen til data/roykprove/kjoringer.jsonl; da
regnes alle kjøringene som gjennomført i pass 1 med PR-tekst.

Standardfeil og intervaller følger Miller, «Adding Error Bars to Evals: A Statistical Approach to Language Model
Evaluations», arXiv:2411.00640v1:
- Oppgavens skår s_i er gjennomsnittet av de K kjøringene for oppgaven (avsnitt 3.1, «Resampling»: «the score s_i is
  the mean of these K answer scores»). K kan variere når kjøringer mangler.
- Gjennomsnitt over oppgaver og standardfeil etter sentralgrenseteoremet: likning (1),
  SE = sqrt( (1/(n-1)) * sum_i (s_i - s̄)^2 / n ).
- 95 %-intervall: likning (3), s̄ ± 1,96 × SE.
- Klyngede standardfeil (klynge = repo): likning (4), SE = sqrt( SE_CLT^2 + (1/n^2) * sum_c sum_i sum_{j≠i}
  (s_ic - s̄)(s_jc - s̄) ), der SE_CLT er fra likning (1). Vedlegg A utleder samme uttrykk, men med første ledd
  sum (s_i - s̄)^2 / n^2 (n, ikke n-1); her brukes likning (4) slik den står (ført som åpent punkt).
- Parvise differanser per oppgave: likning (7), SE = sqrt( (1/(n-1)) * sum_i (d_i - d̄)^2 / n ), d_i = s_A,i - s_B,i.
- Parvise differanser klynget på repo: likning (8), SE = (1/n) * sqrt( sum_c sum_i sum_j (d_ic - d̄)(d_jc - d̄) ).

Bare fullførte pass (p3_pass.jsonl, fullfort = true) inngår i hovedtallene. Manglende kjøringer, forkastede forsøk og
ufullstendige pass rapporteres for seg.

Regler for snitt og differanser:
- En oppgave uten gjennomførte kjøringer i en arm og tekstvariant inngår ikke i snittet for den; antallet (og hvilke)
  oppgis i «oppgaver_uten_gjennomforte_kjoringer».
- Differanser mellom tekstvariantene regnes bare fra pass som har begge variantene (ikke fra pass med bare utvidet tekst).
- Kostnad per løste oppgave oppgis ikke når ingen kjøring er løst; samlet kostnad oppgis i stedet.

    python analysis/analyse.py <p3_kjoringer.jsonl> [--pass p3_pass.jsonl] [--data data] [--ut resultat.json]
"""
import argparse
import collections
import json
import math
import pathlib
import statistics

Z95 = 1.96  # likning (3)
ARMER = ("claude-sonnet-5-5", "claude-opus-5-5")
VARIANTER = ("pr_tekst", "utvidet")
GRENSER = ["Fem repoer gir fem klynger; klyngede standardfeil med så få klynger er usikre (Miller avsnitt 2.2 forutsetter "
           "uavhengige klynger).", "Tallene er beskrivende (NTB-0008); det er ingen hypotesetester."]


# ---------- Miller ----------

def se_clt(s):
    """Likning (1)."""
    n = len(s)
    if n < 2:
        return None
    m = sum(s) / n
    return math.sqrt(sum((x - m) ** 2 for x in s) / (n - 1) / n)


def se_klynget(s, klynger):
    """Likning (4): SE_clustered^2 = SE_CLT^2 + (1/n^2) * sum_c sum_i sum_{j≠i} (s_ic - s̄)(s_jc - s̄)."""
    n = len(s)
    base = se_clt(s)
    if base is None:
        return None
    m = sum(s) / n
    grupper = collections.defaultdict(list)
    for x, c in zip(s, klynger):
        grupper[c].append(x - m)
    kryss = sum(sum(u) ** 2 - sum(v * v for v in u) for u in grupper.values())  # sum_i sum_{j≠i} u_i u_j
    v = base ** 2 + kryss / n ** 2
    return math.sqrt(v) if v > 0 else 0.0


def se_parvis(d):
    """Likning (7)."""
    return se_clt(d)


def se_parvis_klynget(d, klynger):
    """Likning (8): (1/n) * sqrt( sum_c sum_i sum_j (d_ic - d̄)(d_jc - d̄) )."""
    n = len(d)
    if n < 2:
        return None
    m = sum(d) / n
    grupper = collections.defaultdict(float)
    for x, c in zip(d, klynger):
        grupper[c] += x - m
    return math.sqrt(sum(g * g for g in grupper.values())) / n


def intervall(m, se):
    return None if se is None else [round(m - Z95 * se, 4), round(m + Z95 * se, 4)]


# ---------- data ----------

def jl(p):
    p = pathlib.Path(p)
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.is_file() else []


def kort_id(r):
    return f"{r['org']}__{r['repo'].split('/')[1]}__{r['pr']}"


def les(kjoringer, pass_fil, data):
    rader = jl(kjoringer)
    røyk = rader and "tekstvariant" not in rader[0]
    if røyk:  # data/roykprove/kjoringer.jsonl
        rader = [{**r, "pass": 1, "tekstvariant": "pr_tekst", "arm": r["modell"], "status": "gjennomfort"} for r in rader]
        fullførte = {1}
    else:
        fullførte = {p["pass"] for p in jl(pass_fil) if p.get("fullfort")} if pass_fil else {r["pass"] for r in rader}
    sett = {kort_id(r): r for r in jl(pathlib.Path(data) / "sett_v1.jsonl")}
    flagg = {}
    for r in jl(pathlib.Path(data) / "kvalitet/uavhengig_utvidet.jsonl"):
        i = r["id"].replace("nortrebenk__", "")
        flagg[i] = r.get("stemmer_for_utelukkelse") == "ja"
    return rader, fullførte, sett, flagg


def pass_med_begge_varianter(rader):
    """Pass der kjøringene (uansett status) omfatter begge tekstvariantene."""
    v = collections.defaultdict(set)
    for r in rader:
        v[r["pass"]].add(r["tekstvariant"])
    return {p for p, x in v.items() if set(VARIANTER) <= x}


def oppgaveskår(rader, arm, variant):
    """s_i = andel løste av de gjennomførte kjøringene for oppgaven (Miller avsnitt 3.1)."""
    per = collections.defaultdict(list)
    for r in rader:
        if r["arm"] == arm and r["tekstvariant"] == variant and r["status"] == "gjennomfort":
            per[r["oppgave"]].append(1.0 if r.get("loest") else 0.0)
    return {o: sum(v) / len(v) for o, v in per.items()}


def repo_av(oid, sett):
    return sett[oid]["repo"] if oid in sett else oid.rsplit("__", 1)[0].replace("__", "/", 1)


def oppsummer(rader, sett, arm, variant):
    """Oppgavene som telles, er de som har minst én kjøring (uansett status) i arm og tekstvariant; de uten
    gjennomførte kjøringer står utenfor snittet og oppgis."""
    alle = sorted({r["oppgave"] for r in rader if r["arm"] == arm and r["tekstvariant"] == variant})
    if not alle:
        return None
    s = oppgaveskår(rader, arm, variant)
    uten = [i for i in alle if i not in s]
    if not s:
        return {"oppgaver": 0, "oppgaver_uten_gjennomforte_kjoringer": {"antall": len(uten), "oppgaver": uten}}
    ider = sorted(s); v = [s[i] for i in ider]; kl = [repo_av(i, sett) for i in ider]
    m = sum(v) / len(v)
    se, sek = se_clt(v), se_klynget(v, kl)
    mine = [r for r in rader if r["arm"] == arm and r["tekstvariant"] == variant and r["status"] == "gjennomfort"]
    kost = sum(r.get("total_cost_usd") or 0 for r in mine)
    løste = sum(1 for r in mine if r.get("loest"))
    tider = sorted(r.get("veggtid_s") for r in mine if r.get("veggtid_s") is not None)
    kv = statistics.quantiles(tider, n=4, method="inclusive") if len(tider) >= 2 else [None, tider[0] if tider else None, None]
    return {"oppgaver": len(v), "oppgaver_uten_gjennomforte_kjoringer": {"antall": len(uten), "oppgaver": uten},
            "kjoringer": len(mine), "loest_andel": round(m, 4),
            "se_per_oppgave": None if se is None else round(se, 4), "intervall_per_oppgave": intervall(m, se),
            "se_klynget_repo": None if sek is None else round(sek, 4), "intervall_klynget_repo": intervall(m, sek),
            "kostnad_usd": round(kost, 4), "loste_kjoringer": løste,
            **({"kostnad_per_loste_usd": round(kost / løste, 4)} if løste else
               {"kostnad_per_loste_usd": None, "merknad_kostnad": "ingen løste kjøringer; samlet kostnad oppgis i stedet"}),
            "veggtid_s": {"median": statistics.median(tider) if tider else None, "q1": kv[0], "q3": kv[2]}}


def parvis(rader, sett, a, b):
    """Differanse s_a,i - s_b,i for oppgaver som har begge; a og b er (arm, variant)."""
    sa, sb = oppgaveskår(rader, *a), oppgaveskår(rader, *b)
    ider = sorted(set(sa) & set(sb))
    if not ider:
        return None
    d = [sa[i] - sb[i] for i in ider]; kl = [repo_av(i, sett) for i in ider]
    m = sum(d) / len(d)
    se, sek = se_parvis(d), se_parvis_klynget(d, kl)
    return {"merknad": "beskrivende", "oppgaver": len(d), "differanse": round(m, 4),
            "se_per_oppgave": None if se is None else round(se, 4), "intervall_per_oppgave": intervall(m, se),
            "se_klynget_repo": None if sek is None else round(sek, 4), "intervall_klynget_repo": intervall(m, sek),
            "per_oppgave": {i: round(x, 4) for i, x in zip(ider, d)}}


def tabell(rader, sett):
    ut = {f"{a}|{v}": oppsummer(rader, sett, a, v) for a in ARMER for v in VARIANTER}
    par = {}
    for v in VARIANTER:
        par[f"opus_minus_sonnet|{v}"] = parvis(rader, sett, (ARMER[1], v), (ARMER[0], v))
    begge = pass_med_begge_varianter(rader)
    rader_begge = [r for r in rader if r["pass"] in begge]
    for a in ARMER:
        d = parvis(rader_begge, sett, (a, "utvidet"), (a, "pr_tekst"))
        par[f"utvidet_minus_pr_tekst|{a}"] = d and {**d, "pass": sorted(begge)}
    return {"per_arm_og_variant": ut, "parvise_differanser": par}


def analyse(kjoringer, pass_fil=None, data="data"):
    rader, fullførte, sett, flagg = les(kjoringer, pass_fil, data)
    hoved = [r for r in rader if r["pass"] in fullførte]
    res = {"grenser": GRENSER, "fullforte_pass": sorted(fullførte), "hovedtall": tabell(hoved, sett)}
    inndeling = {
        "utfall_p23": lambda o: sett.get(o, {}).get("utfall_p23"),
        "flagget_uavhengig": lambda o: ("ja" if flagg.get(o) else "nei") if flagg else None,
        "repo": lambda o: repo_av(o, sett),
        "tekstsprak": lambda o: sett.get(o, {}).get("tekstsprak"),
        "agentmarkor": lambda o: sett.get(o, {}).get("agentmarkor"),
    }
    res["inndelt"] = {}
    for navn, f in inndeling.items():
        grupper = collections.defaultdict(list)
        for r in hoved:
            grupper[f(r["oppgave"])].append(r)
        res["inndelt"][navn] = {str(k): tabell(v, sett) for k, v in grupper.items() if k is not None}
    if flagg:
        uten = [r for r in hoved if not flagg.get(r["oppgave"])]
        res["hovedmaal_uten_flaggede"] = {f"{a}|utvidet": oppsummer(uten, sett, a, "utvidet") for a in ARMER}
    ufull = [r for r in rader if r["pass"] not in fullførte]
    res["for_seg"] = {
        "manglende_kjoringer": [{k: r.get(k) for k in ("pass", "nummer", "oppgave", "tekstvariant", "arm", "grunn")}
                                for r in rader if r["status"] == "manglende"],
        "forkastede_forsok": {"antall": sum(1 for r in rader if r["status"] == "forkastet"),
                              "kostnad_usd": round(sum(r.get("total_cost_usd") or 0 for r in rader if r["status"] == "forkastet"), 4)},
        "ufullstendige_pass": sorted({r["pass"] for r in ufull}),
        "ufullstendige_pass_tall": tabell(ufull, sett) if ufull else None,
    }
    return res


def main():
    a = argparse.ArgumentParser()
    a.add_argument("kjoringer"); a.add_argument("--pass", dest="pass_fil", default=None)
    a.add_argument("--data", default=str(pathlib.Path(__file__).resolve().parents[1] / "data")); a.add_argument("--ut", default=None)
    o = a.parse_args()
    res = analyse(o.kjoringer, o.pass_fil, o.data)
    tekst = json.dumps(res, ensure_ascii=False, indent=1)
    if o.ut:
        pathlib.Path(o.ut).write_text(tekst, encoding="utf-8")
    print(tekst)


if __name__ == "__main__":
    main()
