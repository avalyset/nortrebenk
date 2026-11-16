#!/usr/bin/env python3
"""P2.4 C6: kjoringer.jsonl (uten transkripter) og budsjett.md fra kjøringsfilene.

    python c6_budsjett.py <kjoringer-mappe> <ut-mappe> <gjenstående_anthropic_usd>
"""
import json
import pathlib
import sys

FELT = ["kjoring", "oppgave", "url", "modell", "budsjett_usd", "claude_code", "total_cost_usd", "usage", "modelUsage",
        "num_turns", "duration_ms", "subtype", "is_error", "veggtid_s", "budsjettak_slo_inn", "tidstak_slo_inn",
        "mellomtjener_kall", "mellomtjener_avvist", "patch_linjer", "forkastede_testfilendringer", "loest", "ikke_pass"]


def main(inn, ut, saldo):
    saldo = float(saldo)
    rader = [json.loads(f.read_text()) for f in sorted(pathlib.Path(inn).glob("*.json"))]
    ut = pathlib.Path(ut); ut.mkdir(parents=True, exist_ok=True)
    with open(ut / "kjoringer.jsonl", "w", encoding="utf-8") as f:
        for r in rader:
            f.write(json.dumps({k: r.get(k) for k in FELT}, ensure_ascii=False) + "\n")
    armer = sorted({r["modell"] for r in rader})
    L = ["# Budsjett fra røykprøven (P2.4)", "",
         f"Målt på {len(rader)} kjøringer: {len({r['oppgave'] for r in rader})} røykprøveoppgaver utenfor settet, én kjøring per arm og oppgave. "
         "Kostnad er `total_cost_usd` fra Claude Code. Bare tall, ingen anbefaling.", "",
         "## Per kjøring", "", "| Oppgave | Arm | Kostnad (USD) | Turer | Veggtid (s) | Løst | Budsjettak | Tidstak |", "|---|---|---|---|---|---|---|---|"]
    for r in rader:
        L.append(f"| {r['url']} | {r['modell']} | {r['total_cost_usd']:.4f} | {r['num_turns']} | {r['veggtid_s']} | "
                 f"{'ja' if r['loest'] else 'nei'} | {'ja' if r['budsjettak_slo_inn'] else 'nei'} | {'ja' if r['tidstak_slo_inn'] else 'nei'} |")
    L += ["", "## Per arm", "", "| Arm | Kjøringer | Snitt kostnad (USD) | Høyeste kostnad (USD) | Snitt veggtid (s) |", "|---|---|---|---|---|"]
    snitt, maks = {}, {}
    for a in armer:
        k = [r["total_cost_usd"] for r in rader if r["modell"] == a]; v = [r["veggtid_s"] for r in rader if r["modell"] == a]
        snitt[a], maks[a] = sum(k) / len(k), max(k)
        L.append(f"| {a} | {len(k)} | {snitt[a]:.4f} | {maks[a]:.4f} | {sum(v) / len(v):.1f} |")
    runde = {"målt snitt": 21 * sum(snitt.values()), "snitt × 1,3": 21 * 1.3 * sum(snitt.values()),
             "høyeste målte": 21 * sum(maks.values())}
    L += ["", f"## Én runde: 21 oppgaver × {len(armer)} armer", "",
          f"Gjenstående Anthropic-saldo ved avlesning etter P2.4: {saldo:.2f} USD (kampanjekreditt og kjøpt saldo).", "",
          "| Grunnlag | Sum for én runde (USD) | Hele runder saldoen dekker |", "|---|---|---|"]
    for n, s in runde.items():
        L.append(f"| {n} | {s:.2f} | {int(saldo // s)} |")
    L += ["", "Grense: grunnlaget er to oppgaver utenfor settet og én kjøring per arm og oppgave."]
    (ut / "budsjett.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main(*sys.argv[1:])
