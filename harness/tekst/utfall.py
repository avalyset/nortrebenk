#!/usr/bin/env python3
"""P2.3b: utfall av kvalitetssjekken av den utvidede teksten (NTB-0004, NTB-0013).

Regel «minst 2 av 3»: en oppgave utelukkes når minst to vurderere stemmer for utelukkelse (skår 2 eller 3) på samme
kriterium. OpenAI-vurdereren kalles bare der nøyaktig én av de to andre stemmer for utelukkelse på et kriterium.

Utfall per oppgave:
- tillegg_feilet: tillegget besto ikke de mekaniske kontrollene etter to forsøk;
- utelukket: to stemmer for utelukkelse på et kriterium;
- uavklart: OpenAI-stemmen mangler der den kunne endret utfallet (består ikke);
- består: ellers.

Underkommandoer:
  avgjorende <svarrot> <utvidet_tekst.jsonl>       skriver id-ene der OpenAI-stemmen kan endre utfallet, sortert
  utfall <svarrot> <utvidet_tekst.jsonl> <p23-vurderinger.jsonl> <ut-mappe>
          skriver vurderinger_utvidet.jsonl og utvidet.md
"""
import json
import pathlib
import sys

KRIT = ("underspecified", "false_negative")
A, O, G = "anthropic:claude-sonnet-5-5", "openai:gpt-6.1-sol", "google:gemini-3.5-flash-lite"


def svar(rot, v, iid):
    f = pathlib.Path(rot) / v.replace(":", "_") / "utvidet" / f"{iid}.json"
    return json.loads(f.read_text()) if f.exists() else None


def stemme(s, k):
    t = (s or {}).get("tolket") or {}
    return isinstance(t.get(k), int) and t[k] >= 2


def avgjørende(rot, iid):
    sa, sg = svar(rot, A, iid), svar(rot, G, iid)
    return [k for k in KRIT if stemme(sa, k) + stemme(sg, k) == 1]


def godkjente(utvidet):
    return [json.loads(l) for l in open(utvidet, encoding="utf-8")]


def utfall_for(rot, r):
    if r["status"] != "godkjent":
        return "tillegg_feilet", [], {}
    iid = r["id"]
    s = {v: svar(rot, v, iid) for v in (A, O, G)}
    stemmer = {k: sum(stemme(s[v], k) for v in (A, O, G) if s[v]) for k in KRIT}
    ute = [k for k in KRIT if stemmer[k] >= 2]
    if ute:
        return "utelukket", ute, stemmer
    avg = avgjørende(rot, iid)
    if avg and s[O] is None:
        return "uavklart", avg, stemmer
    return "består", [], stemmer


def kort(iid):
    return iid.replace("nortrebenk__", "").replace("__", " #", 2).replace(" #", "/", 1)


def main():
    k = sys.argv[1]
    if k == "avgjorende":
        rot, utvidet = sys.argv[2:4]
        for r in sorted(godkjente(utvidet), key=lambda r: r["id"]):
            if r["status"] == "godkjent" and avgjørende(rot, r["id"]):
                print(r["id"])
        return
    rot, utvidet, p23, ut = sys.argv[2:6]
    ut = pathlib.Path(ut); ut.mkdir(parents=True, exist_ok=True)
    rader = godkjente(utvidet)
    gml = {}
    for l in open(p23, encoding="utf-8"):
        x = json.loads(l); gml.setdefault(x["id"], {})[x["vurderer"]] = x
    tabell, teller, openai_kalt = [], {"består": 0, "utelukket": 0, "uavklart": 0, "tillegg_feilet": 0}, []
    with open(ut / "vurderinger_utvidet.jsonl", "w", encoding="utf-8") as f:
        for r in rader:
            iid = r["id"]
            u, på, stemmer = utfall_for(rot, r)
            teller[u] += 1
            if svar(rot, O, iid):
                openai_kalt.append(iid)
            for v in (A, O, G):
                s = svar(rot, v, iid)
                t = (s or {}).get("tolket") or {}
                f.write(json.dumps({"id": iid, "vurderer": v, "kalt": s is not None, "modell_svar": (s or {}).get("modell_svar"),
                                    "parametre": (s or {}).get("parametre"),
                                    "underspecified": t.get("underspecified"), "underspecified_reason": t.get("underspecified_reason"),
                                    "false_negative": t.get("false_negative"), "false_negative_reason": t.get("false_negative_reason"),
                                    "regel": "minst 2 av 3", "stemmer_for_utelukkelse": stemmer, "utfall": u,
                                    "utelukket_paa": på if u == "utelukket" else [], "avgjorende_kriterier": på if u == "uavklart" else []},
                                   ensure_ascii=False) + "\n")
            def sk(kilde, v):
                if kilde == "p23":
                    x = gml.get(iid, {}).get(v)
                    return f"{x['underspecified']}/{x['false_negative']}" if x else "–"
                s = svar(rot, v, iid); t = (s or {}).get("tolket") or {}
                return f"{t.get('underspecified')}/{t.get('false_negative')}" if s else "–"
            p23_utfall = next(iter(gml.get(iid, {}).values()), {}).get("utelukket", "–")
            tabell.append(f"| {kort(iid)} | {sk('p23', A)} | {sk('p23', O)} | {sk('p23', G)} | "
                          f"{'utelukket' if p23_utfall == 'ja' else 'består'} | {sk('ny', A)} | {sk('ny', O)} | {sk('ny', G)} | {u} |")
    L = ["# Kvalitetssjekk av utvidet oppgavetekst (P2.3b)", "",
         "Hver oppgave er vurdert på nytt med den utvidede teksten (PR-teksten med krav og grensesnitt, `data/utvidet_tekst.jsonl`) "
         "i stedet for PR-teksten, med samme prompt, samme vurderere og samme regel («minst 2 av 3») som i P2.3 (NTB-0004, NTB-0013). "
         "OpenAI-vurdereren er bare kalt der nøyaktig én av de to andre stemte for utelukkelse på et kriterium.", "",
         "## Utfall", "",
         f"- består: {teller['består']}", f"- utelukket: {teller['utelukket']}", f"- uavklart: {teller['uavklart']}",
         f"- tillegg_feilet: {teller['tillegg_feilet']}", "",
         "## Per oppgave", "",
         "Skårene er underspecified/false_negative. A = claude-sonnet-5-5, O = gpt-6.1-sol, G = gemini-3.5-flash-lite; «–» = ikke kalt.", "",
         "| Oppgave | A P2.3 | O P2.3 | G P2.3 | Utfall P2.3 | A nå | O nå | G nå | Utfall nå |", "|---|---|---|---|---|---|---|---|---|",
         *tabell, "",
         "## OpenAI-vurdereren kalt for", "", *([f"- {kort(i)}" for i in openai_kalt] or ["- ingen"]), "",
         "## Grenser (NTB-0013)", "",
         "- Endringen er gjort etter at utfallet av P2.3 og røykprøven var kjent, og før noen agentkjøring på oppgavene i settet. "
         "Den er tidsstemplet før tilleggene ble laget.",
         "- Tilleggene er skrevet av en modell fra samme leverandør som agentene (claude-opus-5-5), uten menneskelig kontroll.",
         "- At en oppgave består, kan hvile på vurdereren fra samme leverandør som agentene.",
         "- Tilleggene oppgir navn og strenger fra løsningen.",
         "- Ingen oppgave er fjernet fra `instances.jsonl`; settet fryses i P2.5."]
    (ut / "utvidet.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
