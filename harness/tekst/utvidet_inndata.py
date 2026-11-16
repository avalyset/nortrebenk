#!/usr/bin/env python3
"""P2.3b: inndata til harness/kvalitet/vurder.py for oppgavene med godkjent tillegg (NTB-0013).

Samme felter som harness/kvalitet/egne_inndata.py lager, men med den utvidede teksten i feltet oppgavetekst.

    python utvidet_inndata.py <instances.jsonl> <utvidet_tekst.jsonl> <ut.jsonl>
"""
import json
import sys


def main(instances, utvidet, ut):
    tekst = {}
    for l in open(utvidet, encoding="utf-8"):
        r = json.loads(l)
        if r["status"] == "godkjent":
            tekst[r["id"]] = r["utvidet_tekst"]
    with open(ut, "w", encoding="utf-8") as f:
        for l in open(instances, encoding="utf-8"):
            r = json.loads(l)
            if r["id"] in tekst:
                f.write(json.dumps({"instance_id": r["id"], "oppgavetekst": tekst[r["id"]], "gullpatch": r["gullpatch"],
                                    "testpatch": r["testpatch"], "f2p": r["f2p"]}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:])
