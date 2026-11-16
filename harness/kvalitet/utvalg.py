#!/usr/bin/env python3
"""P2.3 A2: trekk ankerutvalget etter NTB-0004 og hent oppgavedata fra princeton-nlp/SWE-bench (test).

Leser ensembled_annotations_public.csv fra OpenAIs annotasjonsfil (swe-bench-annotation-results.zip). Gruppe «utelukket»:
samleskår (kolonnene underspecified og false_negative) 2 eller høyere på minst ett av de to; gruppe «beholdt»: under 2 på
begge. 50 fra hver, trukket med random.Random(20261116).sample fra sorterte instans-ID-er.

    python utvalg.py <annotasjons-csv> <ut.jsonl>
"""
import csv
import json
import random
import sys

import duckdb

FRØ, N = 20261116, 50
SWEB = "https://huggingface.co/datasets/princeton-nlp/SWE-bench/resolve/main/data/test-00000-of-00001.parquet"


def tall(v):
    return float(v) if v not in (None, "") else None


def main(csvfil, ut):
    csv.field_size_limit(10**9)
    rader = list(csv.DictReader(open(csvfil, newline="", encoding="utf-8")))
    hoy, lav, mangler = [], [], []
    for r in rader:
        u, f = tall(r["underspecified"]), tall(r["false_negative"])
        if u is None or f is None:
            mangler.append(r["instance_id"]); continue
        (hoy if max(u, f) >= 2 else lav).append(r["instance_id"])
    rng = random.Random(FRØ)
    valgt_hoy = rng.sample(sorted(hoy), N)
    valgt_lav = rng.sample(sorted(lav), N)
    print(json.dumps({"annoterte": len(rader), "mangler_skår": len(mangler), "gruppe_2_eller_mer": len(hoy),
                      "gruppe_under_2": len(lav)}, ensure_ascii=False))
    ann = {r["instance_id"]: r for r in rader}
    ids = valgt_hoy + valgt_lav
    con = duckdb.connect(config={"custom_user_agent": "EcoDeco-research/1.0"})
    con.execute("INSTALL httpfs; LOAD httpfs;")
    liste = ",".join("'" + i + "'" for i in ids)
    data = {r[0]: r[1:] for r in con.execute(
        f"SELECT instance_id, problem_statement, patch, test_patch, FAIL_TO_PASS FROM read_parquet('{SWEB}') WHERE instance_id IN ({liste})").fetchall()}
    with open(ut, "w", encoding="utf-8") as fh:
        for i in ids:
            ps, patch, tp, f2p = data[i]
            a = ann[i]
            fh.write(json.dumps({"instance_id": i, "gruppe": "utelukket" if i in valgt_hoy else "beholdt",
                                 "menneske": {"underspecified": tall(a["underspecified"]), "false_negative": tall(a["false_negative"])},
                                 "oppgavetekst": ps, "gullpatch": patch, "testpatch": tp, "f2p": json.loads(f2p)},
                                ensure_ascii=False) + "\n")
    print(f"skrevet {len(ids)} til {ut}; mangler i SWE-bench: {[i for i in ids if i not in data]}")


if __name__ == "__main__":
    main(*sys.argv[1:])
