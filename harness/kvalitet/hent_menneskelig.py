#!/usr/bin/env python3
"""Henter de menneskelige samleskårene for ankerutvalget fra OpenAIs publiserte annotasjonsfil.

Annotasjonsfila oppgir ingen lisens, så skårene distribueres ikke i dette repoet. Skriptet laster ned
swe-bench-annotation-results.zip (lenket fra openai.com/index/introducing-swe-bench-verified/), leser
ensembled_annotations_public.csv og skriver instans-ID og skårene (underspecified, false_negative) for instansene
i data/kvalitet/anker_utvalg.jsonl.

    python hent_menneskelig.py data/kvalitet/anker_utvalg.jsonl menneskelig.jsonl
"""
import csv
import io
import json
import sys
import urllib.request
import zipfile

URL = "https://cdn.openai.com/introducing-swe-bench-verified/swe-bench-annotation-results.zip"


def main(utvalg, ut):
    ids = [json.loads(l)["instance_id"] for l in open(utvalg, encoding="utf-8")]
    req = urllib.request.Request(URL, headers={"User-Agent": "nortrebenk/1.0"})
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req).read()))
    csv.field_size_limit(10**9)
    rader = {r["instance_id"]: r for r in csv.DictReader(io.TextIOWrapper(z.open("ensembled_annotations_public.csv"), encoding="utf-8"))}
    with open(ut, "w", encoding="utf-8") as f:
        for i in ids:
            r = rader[i]
            f.write(json.dumps({"instance_id": i, "underspecified": float(r["underspecified"]),
                                "false_negative": float(r["false_negative"])}) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:])
