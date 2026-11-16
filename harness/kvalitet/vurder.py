#!/usr/bin/env python3
"""P2.3: én vurdering per instans per vurderer med felles prompt (prompt.txt).

Vurderere (modell-ID og parametre føres i hvert svar):
  anthropic:<modell>  Messages API, strukturert JSON-utdata (output_config.format). Temperatur kan ikke settes på
                      Claude Sonnet 5.5 (andre verdier enn standard gir 400), så standard brukes.
  openai:<modell>     Responses API, strukturert JSON-utdata (text.format json_schema). Temperatur 0 forsøkes; avvises
                      den, brukes standard, og det føres i svaret.
  google:<modell>     Gemini API (gratisnivå), JSON-utdata med skjema, temperatur 0. Nøkkelen leses fra ~/.env.

Inndata:
  anker  JSONL fra utvalg.py (instance_id, oppgavetekst, gullpatch, testpatch, f2p)
  egne   JSONL med de samme feltene for egne oppgaver (lages av egne_inndata.py)

    python vurder.py <vurderer> <inndata.jsonl> <svarmappe> [--maks N] [--tak-usd X]

Svar lagres som <svarmappe>/<id>.json (råtekst, tolket JSON, usage, kostnad). Instanser med svar hoppes over.
Kostnad regnes fra usage og prisene i PRISER (USD per million tokens, lest fra leverandørenes prissider).
"""
import argparse
import json
import os
import pathlib
import sys
import time

PROMPT = (pathlib.Path(__file__).parent / "prompt.txt").read_text(encoding="utf-8")
SKJEMA = {"type": "object", "properties": {
    "underspecified": {"type": "integer"}, "underspecified_reason": {"type": "string"},
    "false_negative": {"type": "integer"}, "false_negative_reason": {"type": "string"}},
    "required": ["underspecified", "underspecified_reason", "false_negative", "false_negative_reason"],
    "additionalProperties": False}
# USD per million tokens (inn, ut). Ut inkluderer resonneringstokens.
PRISER = {
    "anthropic:claude-sonnet-5-5": (2.00, 10.00),
    "openai:gpt-6-astra": (10.00, 50.00), "openai:gpt-6.1-sol": (2.00, 10.00),
    "openai:gpt-6.1-terra": (1.00, 5.00), "openai:gpt-6-luna": (0.10, 0.50),
}


def lag_prompt(x):
    return (PROMPT.replace("{oppgavetekst}", x["oppgavetekst"] or "")
            .replace("{gullpatch}", x["gullpatch"]).replace("{testpatch}", x["testpatch"])
            .replace("{f2p}", "\n".join(x["f2p"])))


def anthropic_kall(modell, tekst):
    import anthropic
    k = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY_NORDVAULT"], max_retries=3)
    r = k.messages.create(model=modell, max_tokens=16000, messages=[{"role": "user", "content": tekst}],
                          output_config={"format": {"type": "json_schema", "schema": SKJEMA}})
    svar = next((b.text for b in r.content if b.type == "text"), "")
    u = r.usage
    return {"svar": svar, "stop_reason": r.stop_reason, "modell_svar": r.model,
            "parametre": {"max_tokens": 16000, "temperatur": "standard (kan ikke settes)", "thinking": "standard",
                          "effort": "standard", "output_config.format": "json_schema"},
            "usage": {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                      "cache_creation_input_tokens": u.cache_creation_input_tokens or 0,
                      "cache_read_input_tokens": u.cache_read_input_tokens or 0},
            "inn": u.input_tokens, "ut": u.output_tokens}


def openai_kall(modell, tekst):
    import openai
    k = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"], max_retries=3)
    fmt = {"format": {"type": "json_schema", "name": "vurdering", "schema": SKJEMA, "strict": True}}
    temp = "0"
    try:
        r = k.responses.create(model=modell, input=tekst, text=fmt, temperature=0)
    except openai.BadRequestError as e:
        if "temperature" not in str(e):
            raise
        temp = "standard (temperature avvist av API-et)"
        r = k.responses.create(model=modell, input=tekst, text=fmt)
    u = r.usage
    resonn = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None)
    bufret = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", None)
    return {"svar": r.output_text, "stop_reason": r.status, "modell_svar": r.model,
            "parametre": {"temperatur": temp, "reasoning": "standard", "text.format": "json_schema strict"},
            "usage": {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                      "reasoning_tokens": resonn, "cached_tokens": bufret},
            "inn": u.input_tokens, "ut": u.output_tokens}


def gemini_nokkel():
    """Leser GEMINI_API_KEY fra miljøet eller fra ~/.env (verdien skrives aldri ut)."""
    import re
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    m = re.search(r'^\s*(?:export\s+)?GEMINI_API_KEY\s*=\s*["\']?([^"\'\s]+)', (pathlib.Path.home() / ".env").read_text(), re.M)
    return m.group(1)


def google_kall(modell, tekst):
    from google import genai
    from google.genai import types
    k = genai.Client(api_key=gemini_nokkel())
    time.sleep(5)  # gratisnivået tillater 15 kall per minutt
    skjema = {k2: v for k2, v in SKJEMA.items() if k2 != "additionalProperties"}
    r = k.models.generate_content(model=modell, contents=tekst, config=types.GenerateContentConfig(
        temperature=0, response_mime_type="application/json", response_schema=skjema))
    u = r.usage_metadata
    ut = (u.candidates_token_count or 0) + (u.thoughts_token_count or 0)
    return {"svar": r.text, "stop_reason": str(r.candidates[0].finish_reason) if r.candidates else None,
            "modell_svar": getattr(r, "model_version", modell),
            "parametre": {"temperatur": "0", "response_mime_type": "application/json"},
            "usage": {"prompt_token_count": u.prompt_token_count, "candidates_token_count": u.candidates_token_count,
                      "thoughts_token_count": u.thoughts_token_count},
            "inn": u.prompt_token_count, "ut": ut}


KALL = {"anthropic": anthropic_kall, "openai": openai_kall, "google": google_kall}


def kostnad(vurderer, inn, ut):
    p = PRISER.get(vurderer)
    return round((inn * p[0] + ut * p[1]) / 1e6, 6) if p else 0.0


def main():
    a = argparse.ArgumentParser()
    a.add_argument("vurderer"); a.add_argument("inndata"); a.add_argument("svarmappe")
    a.add_argument("--maks", type=int, default=None); a.add_argument("--tak-usd", type=float, default=None)
    o = a.parse_args()
    lev, modell = o.vurderer.split(":", 1)
    ut = pathlib.Path(o.svarmappe); ut.mkdir(parents=True, exist_ok=True)
    rader = [json.loads(l) for l in open(o.inndata, encoding="utf-8")]
    sum_usd = sum(json.loads(f.read_text())["kostnad_usd"] for f in ut.glob("*.json"))
    n = 0
    for x in rader:
        f = ut / f"{x['instance_id']}.json"
        if f.exists():
            continue
        if o.maks is not None and n >= o.maks:
            break
        if o.tak_usd is not None and sum_usd >= o.tak_usd:
            print(f"STOPP: tak {o.tak_usd} USD nådd ({sum_usd:.4f})"); break
        t0 = time.time()
        try:
            r = KALL[lev](modell, lag_prompt(x))
        except Exception as e:  # noqa: BLE001
            print(f"FEIL {x['instance_id']}: {type(e).__name__}: {str(e)[:300]}", flush=True)
            sys.exit(2)
        try:
            tolket = json.loads(r["svar"])
        except Exception:  # noqa: BLE001
            tolket = None
        r.update(instance_id=x["instance_id"], vurderer=o.vurderer, tolket=tolket,
                 kostnad_usd=kostnad(o.vurderer, r.pop("inn"), r.pop("ut")), sekunder=round(time.time() - t0, 1),
                 tid_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        f.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        sum_usd += r["kostnad_usd"]; n += 1
        print(f"{x['instance_id']}: u={tolket and tolket.get('underspecified')} f={tolket and tolket.get('false_negative')} "
              f"{r['kostnad_usd']:.4f} USD (sum {sum_usd:.4f}) {r['sekunder']} s", flush=True)
    print(f"ferdig: {n} nye, sum {sum_usd:.4f} USD")


if __name__ == "__main__":
    main()
