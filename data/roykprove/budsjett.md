# Budsjett fra røykprøven (P2.4)

Målt på 4 kjøringer: 2 røykprøveoppgaver utenfor settet, én kjøring per arm og oppgave. Kostnad er `total_cost_usd` fra Claude Code. Bare tall, ingen anbefaling.

## Per kjøring

| Oppgave | Arm | Kostnad (USD) | Turer | Veggtid (s) | Løst | Budsjettak | Tidstak |
|---|---|---|---|---|---|---|---|
| https://github.com/Altinn/altinn-access-management-frontend/pull/2552 | claude-opus-5-5 | 0.1678 | 9 | 41.5 | ja | nei | nei |
| https://github.com/Altinn/altinn-access-management-frontend/pull/2552 | claude-sonnet-5-5 | 0.0405 | 4 | 10.8 | nei | nei | nei |
| https://github.com/navikt/mock-oauth2-server/pull/1105 | claude-opus-5-5 | 0.3492 | 17 | 109.9 | ja | nei | nei |
| https://github.com/navikt/mock-oauth2-server/pull/1105 | claude-sonnet-5-5 | 0.0998 | 8 | 59.3 | ja | nei | nei |

## Per arm

| Arm | Kjøringer | Snitt kostnad (USD) | Høyeste kostnad (USD) | Snitt veggtid (s) |
|---|---|---|---|---|
| claude-opus-5-5 | 2 | 0.2585 | 0.3492 | 75.7 |
| claude-sonnet-5-5 | 2 | 0.0702 | 0.0998 | 35.0 |

## Én runde: 21 oppgaver × 2 armer

Gjenstående Anthropic-saldo ved avlesning etter P2.4: 75.07 USD (kampanjekreditt og kjøpt saldo).

| Grunnlag | Sum for én runde (USD) | Hele runder saldoen dekker |
|---|---|---|
| målt snitt | 6.90 | 10 |
| snitt × 1,3 | 8.97 | 8 |
| høyeste målte | 9.43 | 7 |

Grense: grunnlaget er to oppgaver utenfor settet og én kjøring per arm og oppgave.
