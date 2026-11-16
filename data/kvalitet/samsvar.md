# Samsvar mellom vurdererne og de menneskelige Verified-annotasjonene (P2.3)

Ankerutvalget er 100 instanser fra de menneskelig annoterte SWE-bench-instansene (OpenAI, swe-bench-annotation-results.zip): 50 med menneskelig samleskår 2 eller høyere på minst ett av de to kriteriene og 50 under 2 på begge, trukket med frø 20261116 fra sorterte instans-ID-er (NTB-0004). Av 1699 annoterte instanser hadde 1150 samleskår 2 eller høyere og 549 under 2.

Alle vurderere fikk samme prompt (`harness/kvalitet/prompt.txt`), ett kall per instans. En vurderer stemmer for utelukkelse på et kriterium når skåren er 2 eller 3.

## Vurderere

| Vurderer | Parametre |
|---|---|
| claude-sonnet-5-5 (Anthropic) | Messages API, strukturert JSON; temperatur kan ikke settes (standard), thinking og effort standard |
| gpt-6.1-sol (OpenAI) | Responses API, strukturert JSON; temperatur 0 avvist av API-et, standard brukt; reasoning standard |
| gemini-3.5-flash-lite (Google, gratisnivå) | Gemini API, JSON med skjema, temperatur 0 |

## Per vurderer

Andel av de 100 der vurdererens stemme på kriteriet er lik den menneskelige (samleskår 2 eller høyere).

| Vurderer | underspecified | false_negative | Avgjørelse alene |
|---|---|---|---|
| claude-sonnet-5-5 (Anthropic) | 0.76 | 0.79 | 0.78 |
| gpt-6.1-sol (OpenAI) | 0.72 | 0.75 | 0.74 |
| gemini-3.5-flash-lite (Google, gratisnivå) | 0.70 | 0.56 | 0.55 |

## Per regel

Samsvar er andelen av de 100 der ensemblets avgjørelse (utelukket eller beholdt) er lik den menneskelige.

| Regel | Samsvar | Utelukket av 100 |
|---|---|---|
| minst én | 0.75 | 59 |
| minst 2 av 3 | 0.76 | 40 |

**Valgt regel: minst 2 av 3** (høyest samsvar). Regelen ble valgt og lagret før de egne oppgavene ble vurdert.

## Egne oppgaver

Med valgt regel utelukkes 17 av de 21 oppgavene i `instances.jsonl`: 16 på false_negative og Altinn/altinn-support-dashboard #979 på begge kriteriene. Beholdt: navikt/mock-oauth2-server #1069, #1131 og #1154, og Altinn/altinn-support-dashboard #970. Ingen oppgave er fjernet fra `instances.jsonl`; settet fryses i P2.5. Vurderingene står i `vurderinger.jsonl`.

Ordrett andel (andelen av gullpatchens tilføyde linjer, minst 8 tegn, som står ordrett i oppgaveteksten) er over 0 for navikt/mock-oauth2-server #1131 (0,0103) og navikt/pensjonssimulator #688 (0,0169).

## Grenser (NTB-0004)

- Ankeret er engelskspråklige Python-oppgaver som modellene kan ha sett i trening, også med utfallet av annoteringen. Settet er Kotlin og TypeScript med norsk og engelsk tekst.
- Google-vurdereren er en modell på gratisnivået (AVVIK.md), ikke leverandørens sterkeste modell.
- Annotasjonsfila oppgir ingen lisens. De menneskelige skårene er derfor ikke med i `anker_utvalg.jsonl`; `harness/kvalitet/hent_menneskelig.py` henter dem fra kilden.
