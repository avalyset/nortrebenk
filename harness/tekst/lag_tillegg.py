#!/usr/bin/env python3
"""P2.3b (NTB-0013): krav og grensesnitt for hver oppgave, mekaniske kontroller og utvidet oppgavetekst.

For hver oppgave i instances.jsonl: ett kall til claude-opus-5-5 med prompt_tillegg.txt (standardparametre,
strukturert JSON-utdata). Tillegget kontrolleres mekanisk (se kontroller()). Feiler en kontroll, gjøres ett nytt kall
der feilene er oppgitt; feiler det igjen, får oppgaven status tillegg_feilet. Hardt tak på summen fra usage.

Utvidet tekst settes sammen med fast mal: tittel, beskrivelse, «Requirements:» med punktliste og «Interface:» med
oppføringene. Ordrett andel regnes som i P2.3: andelen av gullpatchens tilføyde linjer (uten innledende +, trimmet,
minst 8 tegn) som står ordrett i teksten.

    python lag_tillegg.py <instances.jsonl> <råsvar-mappe> <ut.jsonl> [--tak-usd 4.00]
"""
import argparse
import json
import os
import pathlib
import re
import time

MODELL = "claude-opus-5-5"
PRIS = (4.00, 20.00)  # USD per million tokens inn/ut (platform.claude.com/docs/en/about-claude/pricing, lest 2026-11-16)
PROMPT = (pathlib.Path(__file__).parent / "prompt_tillegg.txt").read_text(encoding="utf-8")
SKJEMA = {"type": "object", "additionalProperties": False, "required": ["requirements", "interface"], "properties": {
    "requirements": {"type": "array", "items": {"type": "string"}},
    "interface": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                             "required": ["type", "name", "location", "inputs", "outputs", "description"],
                                             "properties": {k: {"type": "string"} for k in
                                                            ("type", "name", "location", "inputs", "outputs", "description")}}}}}
EPOST = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
ATNAVN = re.compile(r"(?<![\w.@`])@[A-Za-z0-9][\w-]*")
STI = re.compile(r"(?<![\w/])((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]+)\b")
FORBUDTE_ORD = re.compile(r"\b(tests?|test files?|test cases?|gold patch|golden patch|reference solution|patch)\b", re.I)


def oppgavetekst(r):
    t = r["oppgavetekst"]
    return f"{t['tittel']}\n\n{t['beskrivelse'] or ''}".strip()


def tilføyde(patch):
    return [l[1:].strip() for l in patch.splitlines() if l.startswith("+") and not l.startswith("+++")]


def filer(patch):
    return set(re.findall(r"^diff --git a/\S+ b/(\S+)", patch, re.M))


def tillegg_tekst(t):
    krav = "\n".join(f"- {k}" for k in t["requirements"])
    if t["interface"]:
        gr = "\n\n".join(f"{e['type']}: {e['name']}\nLocation: {e['location']}\nInputs: {e['inputs']}\nOutputs: {e['outputs']}\n"
                         f"Description: {e['description']}" for e in t["interface"])
    else:
        gr = "None."
    return f"Requirements:\n{krav}\n\nInterface:\n{gr}"


def utvidet(r, t):
    return f"{oppgavetekst(r)}\n\nRequirements:\n" + tillegg_tekst(t).split("Requirements:\n", 1)[1]


def ordrett(gullpatch, tekst):
    linjer = [l for l in tilføyde(gullpatch) if len(l) >= 8]
    return (round(sum(1 for l in linjer if l in tekst) / len(linjer), 4) if linjer else 0.0)


def navn_finnes(navn, kilde):
    deler = [d for d in re.split(r"[^\w$]+", re.sub(r"\(.*\)", "", navn)) if len(d) >= 2]
    mangler = [d for d in deler if d not in kilde]
    return not mangler and bool(deler), mangler


def kontroller(r, t):
    """Returnerer {kontroll: (bestått, detalj)}."""
    tekst = tillegg_tekst(t)
    gull = r["gullpatch"]; test = r["testpatch"]
    res = {}
    res["ingen_kodeblokker"] = ("```" not in tekst, None)
    gull20 = {l for l in tilføyde(gull) if len(l) >= 20}
    like = [l.strip() for l in tekst.splitlines() if l.strip() in gull20]
    for felt in t["requirements"] + [e[k] for e in t["interface"] for k in e]:
        if felt.strip() in gull20:
            like.append(felt.strip())
    res["ingen_linje_lik_gullinje_20"] = (not like, like[:3] or None)
    manglende_navn = {}
    for e in t["interface"]:
        ok, mangler = navn_finnes(e["name"], gull + test)
        if not ok:
            manglende_navn[e["name"]] = mangler
    res["navn_i_grensesnitt_finnes_i_patchene"] = (not manglende_navn, manglende_navn or None)
    gfiler = filer(gull)
    stier = {e["location"].strip() for e in t["interface"]} | set(STI.findall(tekst))
    feil_stier = sorted(s for s in stier if s not in gfiler)
    res["filstier_finnes_i_gullpatchen"] = (not feil_stier, feil_stier or None)
    kode = gull + test
    atnavn = [a for a in ATNAVN.findall(tekst) if a not in kode]
    res["ingen_at_navn_eller_epost"] = (not atnavn and not EPOST.search(tekst), (atnavn + EPOST.findall(tekst)) or None)
    return res


def merknader(t):
    """Til opplysning, ikke del av godkjenningen (NTB-0013 har fire mekaniske kontroller, prompten en for @-navn og e-post)."""
    return {"ord_som_kan_omtale_tester_eller_patch": FORBUDTE_ORD.findall(tillegg_tekst(t))[:10]}


def kall(klient, tekst):
    r = klient.messages.create(model=MODELL, max_tokens=16000, messages=[{"role": "user", "content": tekst}],
                               output_config={"format": {"type": "json_schema", "schema": SKJEMA}})
    svar = next((b.text for b in r.content if b.type == "text"), "")
    u = r.usage
    kost = (u.input_tokens * PRIS[0] + u.output_tokens * PRIS[1]) / 1e6
    return svar, r.stop_reason, r.model, {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens}, kost


def main():
    a = argparse.ArgumentParser()
    a.add_argument("instances"); a.add_argument("raa"); a.add_argument("ut"); a.add_argument("--tak-usd", type=float, default=4.00)
    o = a.parse_args()
    import anthropic
    klient = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY_NORDVAULT"], max_retries=3)
    raa = pathlib.Path(o.raa); raa.mkdir(parents=True, exist_ok=True)
    rader = [json.loads(l) for l in open(o.instances, encoding="utf-8")]
    sum_usd = sum(json.loads(f.read_text())["kostnad_usd"] for f in raa.glob("*.json"))
    maks_kall = max([json.loads(f.read_text())["kostnad_usd"] for f in raa.glob("*.json")] or [0.3])
    ut = []
    for r in rader:
        f2p = "\n".join(r["f2p"])
        grunn = (PROMPT.replace("{oppgavetekst}", oppgavetekst(r)).replace("{gullpatch}", r["gullpatch"])
                 .replace("{testpatch}", r["testpatch"]).replace("{f2p}", f2p))
        resultat = {"id": r["id"], "modell": MODELL, "parametre": {"max_tokens": 16000, "thinking": "standard", "effort": "standard",
                                                                  "output_config.format": "json_schema"}, "forsok": 0}
        tekst, t, kontroll = grunn, None, None
        for forsøk in (1, 2):
            f = raa / f"{r['id']}__forsok{forsøk}.json"
            if f.exists():
                lagret = json.loads(f.read_text())
            else:
                if sum_usd + maks_kall > o.tak_usd:
                    print(f"STOPP: taket {o.tak_usd} USD nås (sum {sum_usd:.4f})", flush=True); break
                t0 = time.time()
                svar, stopp, modell_svar, usage, kost = kall(klient, tekst)
                lagret = {"id": r["id"], "forsok": forsøk, "svar": svar, "stop_reason": stopp, "modell_svar": modell_svar,
                          "usage": usage, "kostnad_usd": round(kost, 6), "sekunder": round(time.time() - t0, 1),
                          "tid_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                f.write_text(json.dumps(lagret, ensure_ascii=False, indent=1), encoding="utf-8")
                sum_usd += kost; maks_kall = max(maks_kall, kost)
            resultat["forsok"] = forsøk
            try:
                t = json.loads(lagret["svar"])
            except Exception:  # noqa: BLE001
                t = None
            if t is None:
                kontroll = {"gyldig_json": (False, lagret.get("stop_reason"))}
            else:
                kontroll = kontroller(r, t)
            feil = {k: v[1] for k, v in kontroll.items() if not v[0]}
            print(f"{r['id']} forsøk {forsøk}: {'godkjent' if not feil else 'feil: ' + ', '.join(feil)} "
                  f"({lagret['kostnad_usd']:.4f} USD, sum {sum_usd:.4f})", flush=True)
            if not feil:
                break
            tekst = (grunn + "\n\nA previous answer to this request failed these mechanical checks, listed as check name and "
                     "offending values. Write the two sections again and make sure every check passes:\n"
                     + json.dumps(feil, ensure_ascii=False))
        godkjent = bool(kontroll) and all(v[0] for v in kontroll.values())
        resultat.update(status="godkjent" if godkjent else ("tillegg_feilet" if resultat["forsok"] else "ikke_kjort"),
                        kontroller={k: {"bestatt": v[0], "detalj": v[1]} for k, v in (kontroll or {}).items()})
        if t is not None:
            resultat.update(requirements=t["requirements"], interface=t["interface"], merknader=merknader(t))
        if godkjent:
            ut_tekst = utvidet(r, t)
            resultat.update(utvidet_tekst=ut_tekst, ordrett_andel=ordrett(r["gullpatch"], ut_tekst))
        ut.append(resultat)
    with open(o.ut, "w", encoding="utf-8") as fh:
        for x in ut:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"ferdig: {sum(1 for x in ut if x['status'] == 'godkjent')} godkjent, sum {sum_usd:.4f} USD")


if __name__ == "__main__":
    main()
