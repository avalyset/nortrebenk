#!/usr/bin/env python3
"""P2.3 A6–A7: sammenstill vurderingene til de offentlige filene under data/kvalitet/.

- anker_utvalg.jsonl: instans-ID, gruppe og vurdererskårer for ankerutvalget. De menneskelige skårene tas ikke med,
  fordi annotasjonsfila fra OpenAI ikke oppgir lisens; hent_menneskelig.py henter dem fra kilden.
- vurderinger.jsonl: én linje per egen oppgave og vurderer, med skårer og begrunnelse, valgt regel, utelukket ja/nei
  for ensemblet og det mekaniske feltet «ordrett andel».
- samsvar.md: samsvaret på ankeret per vurderer og per regel, valgt regel og grensene fra NTB-0004.

Ordrett andel: andelen av gullpatchens tilføyde linjer (uten innledende +, trimmet, minst 8 tegn) som står ordrett
i oppgaveteksten (tittel og beskrivelse).

    python sammenstill.py <anker_utvalg_full.jsonl> <egne_inndata.jsonl> <svarrot> <samsvar_anker.json> <ut-mappe>
"""
import json
import pathlib
import sys

KRIT = ("underspecified", "false_negative")


def ordrett(gullpatch, tekst):
    linjer = [l[1:].strip() for l in gullpatch.splitlines() if l.startswith("+") and not l.startswith("+++")]
    linjer = [l for l in linjer if len(l) >= 8]
    if not linjer:
        return 0.0, 0, 0
    treff = sum(1 for l in linjer if l in tekst)
    return round(treff / len(linjer), 4), treff, len(linjer)


def main(anker_fil, egne_fil, svarrot, samsvar_fil, ut):
    ut = pathlib.Path(ut); ut.mkdir(parents=True, exist_ok=True)
    s = json.loads(pathlib.Path(samsvar_fil).read_text())
    vurderere, k = s["vurderere"], s["valgt_k"]
    hent = lambda v, sett, iid: json.loads((pathlib.Path(svarrot) / v.replace(":", "_") / sett / f"{iid}.json").read_text())
    with open(ut / "anker_utvalg.jsonl", "w", encoding="utf-8") as f:
        for l in open(anker_fil, encoding="utf-8"):
            a = json.loads(l)
            rad = {"instance_id": a["instance_id"], "gruppe": a["gruppe"], "vurderinger": {}}
            for v in vurderere:
                t = hent(v, "anker", a["instance_id"]).get("tolket") or {}
                rad["vurderinger"][v] = {k2: t.get(k2) for k2 in KRIT}
            f.write(json.dumps(rad, ensure_ascii=False) + "\n")
    with open(ut / "vurderinger.jsonl", "w", encoding="utf-8") as f:
        for l in open(egne_fil, encoding="utf-8"):
            x = json.loads(l)
            andel, treff, n = ordrett(x["gullpatch"], x["oppgavetekst"])
            stemmer = {k2: 0 for k2 in KRIT}
            svar = {}
            for v in vurderere:
                sv = hent(v, "egne", x["instance_id"])
                t = sv.get("tolket") or {}
                for k2 in KRIT:
                    stemmer[k2] += isinstance(t.get(k2), int) and t[k2] >= 2
                svar[v] = sv
            utelukket_på = [k2 for k2 in KRIT if stemmer[k2] >= k]
            for v in vurderere:
                sv = svar[v]; t = sv.get("tolket") or {}
                f.write(json.dumps({
                    "id": x["instance_id"], "vurderer": v, "modell_svar": sv.get("modell_svar"), "parametre": sv.get("parametre"),
                    "underspecified": t.get("underspecified"), "underspecified_reason": t.get("underspecified_reason"),
                    "false_negative": t.get("false_negative"), "false_negative_reason": t.get("false_negative_reason"),
                    "valgt_regel": s["valgt_regel"], "stemmer_for_utelukkelse": stemmer,
                    "utelukket": "ja" if utelukket_på else "nei", "utelukket_paa": utelukket_på,
                    "ordrett_andel": andel, "ordrett_linjer": treff, "tilfoyde_linjer_minst_8_tegn": n,
                }, ensure_ascii=False) + "\n")
    print("skrevet", ut)


if __name__ == "__main__":
    main(*sys.argv[1:])
