# NTB-0004: Quality check

- Status: adopted 2026-11-16
- Changed 2026-11-16: score threshold and merge rule clarified.
- Changed 2026-11-16 (2): anchor sample, agreement measure and judges clarified.
- Changed 2026-11-16 (3): the OpenAI judge is called only where its vote can change the outcome, see NTB-0013.

## Context

The task text is the PR description, which may describe the solution or be too vague. The tests may also reject valid solutions. SWE-bench Verified used human annotators with a rubric for these conditions.

## Decision

Each task is assessed on the two criteria in the SWE-bench Verified rubric (underspecified task text; tests that reject valid solutions), with score 0–3, by three models from different vendors with the rubric as the prompt. A model votes for exclusion on a criterion when it gives score 2 or 3. The merge rule is chosen on the anchor sample from the human Verified annotations, before it is applied to our own tasks: either a task is excluded when at least one of three models votes for exclusion on a criterion, or when at least two of three do. The rule with the highest agreement with the human annotations is chosen; with equal agreement the strictest is chosen. The ensemble is first measured against the published human Verified annotations. In addition, two mechanical fields are recorded per task: the share of the gold patch's added lines that appear verbatim in the task text, and whether the test patch compiles against base. All assessments are published. The author is not a judge.

The anchor sample is 100 instances drawn from the human-annotated SWE-bench instances: 50 where the human combined score is 2 or higher on at least one of the two criteria, and 50 where it is below 2 on both, drawn with a fixed seed (20261116) from sorted instance IDs. Agreement is the share of the 100 where the ensemble's decision (excluded or kept) equals the human one. The judges are one model from Anthropic, one from OpenAI and one from Google; model IDs and parameters are recorded together with the assessments. If a judge cannot be used without expenses beyond existing credit, it is recorded as a deviation, and the rule is chosen between «at least one» and «all» among the judges that remain. The anchor is English-language Python tasks that the models may have seen in training, also with the outcome of the annotation; the set is Kotlin, TypeScript and C# with Norwegian and English text. Both are stated as a limitation.

## Alternatives considered

- The author assesses themselves. Argument against the decision: human assessment is the standard in Verified. Rejected because the author knows the tasks and the outcomes from P1.
- No quality check. Argument against the decision: fewer steps and lower cost. Rejected because PR descriptions may contain the solution.

## Consequences

The quality check (P2.3) uses API credit. The ensemble's agreement with the human annotations is reported before it is applied to the set.

## Sources

- OpenAI, «Introducing SWE-bench Verified», 13.08.2024 (openai.com/index/introducing-swe-bench-verified/), read in browser 16.11.2026. Exclusion at combined score 2 or higher: «have an ensemble label of 2 or above in severity»; merging: «taking the highest-severity label amongst the 3 annotators». The page has no single sentence that says both; the two parts are in separate sentences.
- OpenAI, «Why SWE-bench Verified no longer measures frontier coding capabilities» (page title «Why we no longer evaluate SWE-bench Verified»), 23.02.2026 (openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/), read in browser 16.11.2026: «This is why we have stopped reporting SWE-bench Verified scores»
- «SWE-rebench V2: Language-Agnostic SWE Task Collection at Scale», arXiv:2602.23866 (the abstract; §3.4 could not be quoted verbatim from the PDF text): «filters unsound instances using an ensemble of LLM judges, validated against human-verified SWE-bench annotations»
