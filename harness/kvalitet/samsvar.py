#!/usr/bin/env python3
"""P2.3 A5: samsvar mellom vurdererne og de menneskelige Verified-annotasjonene på ankerutvalget (NTB-0004).

En vurderer stemmer for utelukkelse på et kriterium når skåren er 2 eller 3. Menneskelig utelukkelse på et kriterium:
samleskåren (kolonnene underspecified og false_negative) er 2 eller høyere. Menneskelig avgjørelse for instansen:
utelukket når minst ett kriterium har samleskår 2 eller høyere.

Regler for ensemblet: «minst k av n» betyr at instansen utelukkes når minst k vurderere stemmer for utelukkelse på
samme kriterium, for minst ett av kriteriene. Med tre vurderere sammenlignes k = 1 og k = 2; med to sammenlignes
«minst én» og «alle» (NTB-0004). Høyest samsvar velges; ved likt samsvar velges den strengeste (lavest k).
Et svar som ikke kan tolkes, teller som ingen stemme og telles opp for seg.

    python samsvar.py <anker_utvalg.jsonl> <svarrot> <ut.json> <vurderer>...
"""
import json
import pathlib
import sys

KRIT = ("underspecified", "false_negative")


def main(utvalg, svarrot, ut, *vurderere):
    anker = [json.loads(l) for l in open(utvalg, encoding="utf-8")]
    svar = {v: {} for v in vurderere}
    for v in vurderere:
        for f in (pathlib.Path(svarrot) / v.replace(":", "_") / "anker").glob("*.json"):
            s = json.loads(f.read_text())
            svar[v][s["instance_id"]] = s.get("tolket")
    n = len(anker)
    res = {"n": n, "vurderere": list(vurderere), "per_vurderer": {}, "regler": {}}
    stemme = lambda t, k: bool(t) and isinstance(t.get(k), int) and t[k] >= 2
    for v in vurderere:
        d = {"manglende_svar": sum(1 for a in anker if a["instance_id"] not in svar[v]),
             "ikke_tolkbare": sum(1 for a in anker if a["instance_id"] in svar[v] and not svar[v][a["instance_id"]])}
        for k in KRIT:
            riktig = sum(1 for a in anker if stemme(svar[v].get(a["instance_id"]), k) == (a["menneske"][k] >= 2))
            d[f"riktig_stemme_{k}"] = round(riktig / n, 3)
        d["riktig_avgjorelse_alene"] = round(sum(1 for a in anker if any(stemme(svar[v].get(a["instance_id"]), k) for k in KRIT)
                                              == (a["gruppe"] == "utelukket")) / n, 3)
        res["per_vurderer"][v] = d
    m = len(vurderere)
    kandidater = [1, 2] if m == 3 else ([1, m] if m >= 2 else [1])
    for kmin in kandidater:
        navn = "minst én" if kmin == 1 else ("alle" if kmin == m else f"minst {kmin} av {m}")
        treff, utelukket = 0, 0
        for a in anker:
            ut_ens = any(sum(stemme(svar[v].get(a["instance_id"]), k) for v in vurderere) >= kmin for k in KRIT)
            utelukket += ut_ens
            treff += ut_ens == (a["gruppe"] == "utelukket")
        res["regler"][navn] = {"k": kmin, "samsvar": round(treff / n, 3), "utelukket": utelukket}
    best = max(res["regler"].items(), key=lambda kv: (kv[1]["samsvar"], -kv[1]["k"]))
    res["valgt_regel"] = best[0]
    res["valgt_k"] = best[1]["k"]
    pathlib.Path(ut).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
