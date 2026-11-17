# Quality check of the extended task text (P2.3b)

Each task was assessed again with the extended text (the PR text with requirements and interface, `data/utvidet_tekst.jsonl`) instead of the PR text, with the same prompt, the same raters and the same rule («minst 2 av 3», at least 2 of 3) as in P2.3 (NTB-0004, NTB-0013). The OpenAI rater was called only where exactly one of the other two voted for exclusion on a criterion.

## Outcome

- består: 21
- utelukket: 0
- uavklart: 0
- tillegg_feilet: 0

## Per task

The scores are underspecified/false_negative. A = claude-sonnet-5-5, O = gpt-6.1-sol, G = gemini-3.5-flash-lite; «–» = not called. Outcome values: består = passes, utelukket = excluded.

| Task | A P2.3 | O P2.3 | G P2.3 | Outcome P2.3 | A now | O now | G now | Outcome now |
|---|---|---|---|---|---|---|---|---|
| navikt/mock-oauth2-server #1069 | 1/0 | 0/0 | 0/0 | består | 1/1 | – | 0/0 | består |
| navikt/mock-oauth2-server #1131 | 1/1 | 0/0 | 0/0 | består | 1/1 | – | 0/0 | består |
| navikt/mock-oauth2-server #1154 | 1/1 | 0/0 | 0/0 | består | 1/1 | – | 0/0 | består |
| navikt/mock-oauth2-server #1155 | 2/3 | 0/2 | 0/0 | utelukket | 0/0 | – | 0/0 | består |
| navikt/mock-oauth2-server #1161 | 1/2 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/pensjonssimulator #688 | 2/2 | 1/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/pensjonssimulator #692 | 3/3 | 1/2 | 1/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/pensjonssimulator #702 | 3/3 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/pensjonssimulator #715 | 2/2 | 1/2 | 1/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/kafka-manager #329 | 3/3 | 0/2 | 0/0 | utelukket | 0/0 | – | 0/0 | består |
| navikt/kafka-manager #330 | 3/3 | 0/3 | 1/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/kafka-manager #336 | 3/3 | 1/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/kafka-manager #337 | 2/2 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-support-dashboard #966 | 2/2 | 0/2 | 0/0 | utelukket | 0/1 | – | 0/0 | består |
| Altinn/altinn-support-dashboard #970 | 1/1 | 0/0 | 0/0 | består | 0/0 | – | 0/0 | består |
| Altinn/altinn-support-dashboard #979 | 3/3 | 2/2 | 3/0 | utelukket | 1/0 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2619 | 3/3 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2625 | 2/2 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2642 | 2/3 | 1/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2644 | 3/3 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2645 | 1/2 | 0/2 | 0/0 | utelukket | 0/1 | – | 0/0 | består |

## OpenAI rater called for

- none

## Limits (NTB-0013)

- The change was made after the outcome of P2.3 and the smoke test were known, and before any agent run on the tasks in the set. It was timestamped before the additions were written.
- The additions were written by a model from the same vendor as the agents (claude-opus-5-5), without human review.
- That a task passes may rest on the rater from the same vendor as the agents.
- The additions state names and strings from the solution.
- No task has been removed from `instances.jsonl`; the set is frozen in P2.5.
