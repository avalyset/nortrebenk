# Independent check of the extended text (P2.5)

The OpenAI rater (`gpt-6.1-sol`) assessed the extended task text with the same prompt and output schema as in P2.3 and P2.3b (`harness/kvalitet/prompt.txt`), run through OpenAI's Batch API (endpoint `/v1/responses`). A vote for exclusion is a score of 2 or 3 on at least one of the two criteria. The vote does not change the set, because the rule needs two votes; flagged tasks are marked, and the main measure is reported with and without them (NTB-0013).

- Tasks assessed: 21
- Flagged (vote for exclusion): 0
- Not assessed (request failed in the batch): 0
- Not interpretable: 0
- Cost from usage at the batch price (USD 1.00 / 5.00 per million input/output tokens): 0.2068 USD (191378 input tokens, 3082 output tokens)

## Flagged tasks

- none

## All scores

| Task | underspecified | false_negative | Vote for exclusion |
|---|---|---|---|
| Altinn/altinn-access-management-frontend #2619 | 0 | 0 | nei |
| Altinn/altinn-access-management-frontend #2625 | 0 | 0 | nei |
| Altinn/altinn-access-management-frontend #2642 | 0 | 0 | nei |
| Altinn/altinn-access-management-frontend #2644 | 0 | 0 | nei |
| Altinn/altinn-access-management-frontend #2645 | 0 | 0 | nei |
| Altinn/altinn-support-dashboard #966 | 0 | 0 | nei |
| Altinn/altinn-support-dashboard #970 | 0 | 0 | nei |
| Altinn/altinn-support-dashboard #979 | 0 | 0 | nei |
| navikt/kafka-manager #329 | 0 | 0 | nei |
| navikt/kafka-manager #330 | 0 | 0 | nei |
| navikt/kafka-manager #336 | 0 | 0 | nei |
| navikt/kafka-manager #337 | 0 | 0 | nei |
| navikt/mock-oauth2-server #1069 | 0 | 0 | nei |
| navikt/mock-oauth2-server #1131 | 0 | 0 | nei |
| navikt/mock-oauth2-server #1154 | 0 | 0 | nei |
| navikt/mock-oauth2-server #1155 | 0 | 0 | nei |
| navikt/mock-oauth2-server #1161 | 0 | 0 | nei |
| navikt/pensjonssimulator #688 | 0 | 0 | nei |
| navikt/pensjonssimulator #692 | 0 | 0 | nei |
| navikt/pensjonssimulator #702 | 0 | 0 | nei |
| navikt/pensjonssimulator #715 | 0 | 0 | nei |
