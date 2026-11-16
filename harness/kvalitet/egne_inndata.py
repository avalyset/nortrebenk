#!/usr/bin/env python3
"""Lager inndata til vurder.py for de egne oppgavene fra data/instances.jsonl.
Oppgaveteksten er tittel og beskrivelse slik agenten får dem (NTB-0007).

    python egne_inndata.py <instances.jsonl> <ut.jsonl>
"""
import json
import sys

with open(sys.argv[2], "w", encoding="utf-8") as ut:
    for l in open(sys.argv[1], encoding="utf-8"):
        r = json.loads(l)
        t = r["oppgavetekst"]
        ut.write(json.dumps({"instance_id": r["id"], "oppgavetekst": f"{t['tittel']}\n\n{t['beskrivelse'] or ''}".strip(),
                             "gullpatch": r["gullpatch"], "testpatch": r["testpatch"], "f2p": r["f2p"]},
                            ensure_ascii=False) + "\n")
