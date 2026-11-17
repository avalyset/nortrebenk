*Translated by hand from the Norwegian original in P2.5; no script writes this file.*

# Agreement between the raters and the human Verified annotations (P2.3)

The anchor sample is 100 instances from the human-annotated SWE-bench instances (OpenAI, swe-bench-annotation-results.zip): 50 with a human aggregate score of 2 or higher on at least one of the two criteria and 50 below 2 on both, drawn with seed 20261116 from sorted instance IDs (NTB-0004). Of 1699 annotated instances, 1150 had an aggregate score of 2 or higher and 549 below 2.

All raters got the same prompt (`harness/kvalitet/prompt.txt`), one call per instance. A rater votes for exclusion on a criterion when the score is 2 or 3.

## Raters

| Rater | Parameters |
|---|---|
| claude-sonnet-5-5 (Anthropic) | Messages API, structured JSON; temperature cannot be set (default), thinking and effort default |
| gpt-6.1-sol (OpenAI) | Responses API, structured JSON; temperature 0 rejected by the API, default used; reasoning default |
| gemini-3.5-flash-lite (Google, free tier) | Gemini API, JSON with schema, temperature 0 |

## Per rater

Share of the 100 where the rater's vote on the criterion equals the human one (aggregate score 2 or higher).

| Rater | underspecified | false_negative | Decision alone |
|---|---|---|---|
| claude-sonnet-5-5 (Anthropic) | 0.76 | 0.79 | 0.78 |
| gpt-6.1-sol (OpenAI) | 0.72 | 0.75 | 0.74 |
| gemini-3.5-flash-lite (Google, free tier) | 0.70 | 0.56 | 0.55 |

## Per rule

Agreement is the share of the 100 where the ensemble's decision (excluded or kept) equals the human one.

| Rule | Agreement | Excluded of 100 |
|---|---|---|
| minst én (at least one) | 0.75 | 59 |
| minst 2 av 3 (at least 2 of 3) | 0.76 | 40 |

**Chosen rule: minst 2 av 3 (at least 2 of 3)** (highest agreement). The rule was chosen and stored before the set's own tasks were assessed.

## The set's own tasks

With the chosen rule, 17 of the 21 tasks in `instances.jsonl` are excluded: 16 on false_negative and Altinn/altinn-support-dashboard #979 on both criteria. Kept: navikt/mock-oauth2-server #1069, #1131 and #1154, and Altinn/altinn-support-dashboard #970. No task has been removed from `instances.jsonl`; the set is frozen in P2.5. The ratings are in `vurderinger.jsonl`.

Verbatim share (the share of the gold patch's added lines, at least 8 characters, that appear verbatim in the task text) is above 0 for navikt/mock-oauth2-server #1131 (0.0103) and navikt/pensjonssimulator #688 (0.0169).

## Limits (NTB-0004)

- The anchor consists of English-language Python tasks that the models may have seen in training, including the outcome of the annotation. The set is Kotlin and TypeScript with Norwegian and English text.
- The Google rater is a free-tier model (AVVIK.md), not the vendor's strongest model.
- The annotation file states no licence. The human scores are therefore not included in `anker_utvalg.jsonl`; `harness/kvalitet/hent_menneskelig.py` fetches them from the source.
