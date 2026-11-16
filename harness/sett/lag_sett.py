#!/usr/bin/env python3
"""Setter sammen data/sett_v1.jsonl fra eksisterende datafiler (NTB-0003, NTB-0013).

En oppgave er med når den består kvalitetssjekken av den utvidede teksten (data/kvalitet/vurderinger_utvidet.jsonl,
utfall «består»). Patchene står i data/instances.jsonl; her står bare sha256 for dem. For oppgaver i
data/p24_nett.jsonl tas byggfeltene med (avhengighetscacher fra gulltilstanden og ekstra miljø), fra siste forsøk.
Flagget fra den uavhengige kontrollen står ikke her; analysen leser det fra data/kvalitet/uavhengig_utvidet.jsonl.

    python harness/sett/lag_sett.py [data-mappe]
"""
import json
import pathlib
import sys


def jl(p):
    return [json.loads(l) for l in pathlib.Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def main(data="data"):
    d = pathlib.Path(data)
    inst = jl(d / "instances.jsonl")
    utv = {r["id"]: r for r in jl(d / "utvidet_tekst.jsonl")}
    p23 = {}
    for r in jl(d / "kvalitet/vurderinger.jsonl"):
        p23.setdefault(r["id"], r)
    p23b = {}
    for r in jl(d / "kvalitet/vurderinger_utvidet.jsonl"):
        p23b.setdefault(r["id"], r)
    nett = {}
    for r in jl(d / "p24_nett.jsonl"):
        nett[r["url"]] = r
    ut = []
    for r in inst:
        if p23b.get(r["id"], {}).get("utfall") != "består":
            continue
        rad = {
            "id": r["id"], "repo": r["repo"], "org": r["org"], "url": r["url"], "pr": r["pr"], "base_sha": r["base_sha"],
            "base_image": r["base_image"], "lisens": r["lisens"], "kodesprak": r["kodesprak"], "tekstsprak": r["tekstsprak"],
            "agentmarkor": r["agentmarkor"], "merged": r["merged"],
            "pr_tekst": {"tittel": r["oppgavetekst"]["tittel"], "beskrivelse": r["oppgavetekst"]["beskrivelse"]},
            "utvidet_tekst": utv[r["id"]]["utvidet_tekst"],
            "testpatch_sha256": r["testpatch_sha256"], "gullpatch_sha256": r["gullpatch_sha256"],
            "f2p": r["f2p"], "p2p": r["p2p"],
            "utfall_p23": "utelukket" if p23[r["id"]]["utelukket"] == "ja" else "består",
            "utfall_p23b": p23b[r["id"]]["utfall"],
            "ordrett_andel_pr_tekst": p23[r["id"]]["ordrett_andel"],
            "ordrett_andel_utvidet": utv[r["id"]]["ordrett_andel"],
            "canary": r["canary"],
        }
        if r["url"] in nett:
            n = nett[r["url"]]
            rad["bygg"] = {"cacher_fra_gulltilstand": n["cacher_fra_gulltilstand"], "ekstra_miljo": n.get("ekstra_miljo"),
                           "kilde": "data/p24_nett.jsonl", "forsok": n.get("forsok")}
        ut.append(rad)
    (d / "sett_v1.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in ut), encoding="utf-8")
    print(f"{len(ut)} oppgaver skrevet til {d / 'sett_v1.jsonl'}")


if __name__ == "__main__":
    main(*sys.argv[1:])
