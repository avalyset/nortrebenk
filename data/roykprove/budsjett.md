# Budget from the smoke test (P2.4)

Measured on 4 runs: 2 smoke-test tasks outside the set, one run per arm and task. Cost is `total_cost_usd` from Claude Code. Numbers only, no recommendation.

## Per run

Yes/no columns: ja = yes, nei = no.

| Task | Arm | Cost (USD) | Turns | Wall time (s) | Solved | Budget cap | Time cap |
|---|---|---|---|---|---|---|---|
| https://github.com/Altinn/altinn-access-management-frontend/pull/2552 | claude-opus-5-5 | 0.1678 | 9 | 41.5 | ja | nei | nei |
| https://github.com/Altinn/altinn-access-management-frontend/pull/2552 | claude-sonnet-5-5 | 0.0405 | 4 | 10.8 | nei | nei | nei |
| https://github.com/navikt/mock-oauth2-server/pull/1105 | claude-opus-5-5 | 0.3492 | 17 | 109.9 | ja | nei | nei |
| https://github.com/navikt/mock-oauth2-server/pull/1105 | claude-sonnet-5-5 | 0.0998 | 8 | 59.3 | ja | nei | nei |

## Per arm

| Arm | Runs | Mean cost (USD) | Highest cost (USD) | Mean wall time (s) |
|---|---|---|---|---|
| claude-opus-5-5 | 2 | 0.2585 | 0.3492 | 75.7 |
| claude-sonnet-5-5 | 2 | 0.0702 | 0.0998 | 35.0 |

## One round: 21 tasks × 2 arms

Remaining Anthropic balance when read after P2.4: 75.07 USD (promotional credit and purchased balance).

| Basis | Sum for one round (USD) | Whole rounds the balance covers |
|---|---|---|
| measured mean | 6.90 | 10 |
| mean × 1.3 | 8.97 | 8 |
| highest measured | 9.43 | 7 |

Limit: the basis is two tasks outside the set and one run per arm and task.
