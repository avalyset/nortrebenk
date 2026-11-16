# NTB-0013: Text variants

- Status: adopted 2026-11-16
- Changed 2026-11-16: independent check of the extended text.

## Context

The quality check in P2.3 let 4 of 21 tasks pass. 16 were excluded on the criterion that the tests may reject valid solutions, and one on both criteria. The raters justify the exclusions by saying that the tests require names, file paths, keys or strings that are not in the PR text. Four tasks, three of them from the same repo, give no measurement. SWE-Bench Pro keeps underspecified tasks and extends the task text with requirements and interfaces grounded in the tests.

## Decision

Each task gets two text variants. «PR text» is the title and description as they appear in instances.jsonl. «Extended» is the PR text with two additions following the SWE-Bench Pro pattern: requirements and interface. The requirements state which behavior the fail-to-pass tests check and the PR text does not state, with exact names, keys and strings where the tests require them. The interface lists classes, functions, methods and fields that the tests use and that must be created or changed, with file path, input and output. The additions contain no implementation code and do not mention the tests or the gold patch. They are written in English by one model (claude-opus-5-5) from the PR text, gold patch, test patch and fail-to-pass names, with a fixed prompt, and are checked mechanically: no code blocks, no line equal to an added gold patch line of at least 20 characters, all names in the interface exist in the test patch or the gold patch, and all file paths exist in the gold patch. If the check fails, the addition is written once more; if it fails again, the task does not pass.

The quality requirement in NTB-0003 applies to the extended text. It is assessed with the same prompt, the same three raters and the same rule as in P2.3. The OpenAI rater is called only for tasks where the vote can change the outcome, that is, where exactly one of the other two votes for exclusion on a criterion, because the remaining credit does not cover all of them. If such a vote is missing when the credit is used up, the task does not pass. The limit of 20 in NTB-0003 stands.

In P3 both text variants are run for the tasks in the set. The primary outcome is resolved rate on extended text. The difference between the variants is reported pairwise per task, descriptively, and broken down by the outcome of the quality check of the PR text in P2.3. If the budget does not suffice, runs are cut before a text variant, and the PR-text variant before an arm.

Independent check: the OpenAI rater assesses the extended text with the same prompt, for all tasks in the set if the remaining credit covers it, otherwise for 11 of the 17 that were excluded in P2.3, drawn with seed 20261116 from sorted IDs. The vote does not change the set, because the rule requires two votes. Tasks where it votes for exclusion are marked, and the primary outcome is reported both with and without them.

## Alternatives considered

- Freeze the set with the four that pass with the PR text. Argument against the decision: no change after the outcome is known. Rejected because four tasks do not give a measurement, and because the literature has an established way of correcting underspecified tasks.
- Let humans write the additions, as in SWE-Bench Pro. Argument against the decision: it is the model to follow. Rejected because the author is not a rater (NTB-0004), and the study has no other annotators.
- Run only the PR text on all 21. Argument against the decision: it is the text the agencies actually have. Rejected as the only variant because failures then cannot be distinguished from tests that reject valid solutions; the variant is run as a comparison.

## Consequences

The change was made after the outcome of P2.3 and the smoke trial was known, and before any agent run on the tasks in the set. It is timestamped before the additions were made. The additions are written by a model from the same vendor as the agents, without human checking, and that a task passes may rest on the rater from the same vendor. The additions state names and strings from the solution. All of this is recorded as limitations in the README when the repo's documents are rewritten in P2.5.

## Sources

- Deng et al., «SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?», arXiv:2509.16941v2, §3.2: «These requirements are grounded on the unit tests that are used for validation.»
- Same, appendix B.2: «Requirements never include specific code implementation and don’t leak solutions.»
- Same, table 3 (resolved rate with problem description, requirements and interface versus problem description only): OpenAI GPT-5 (high) 25.9% versus 8.40%; Claude Opus 4.1 22.7% versus 8.20%.
- OpenAI, «SWE-bench Annotation Instructions» (cdn.openai.com/introducing-swe-bench-verified/swe-b-annotation-instructions.pdf): «We find that the most common problems occur when there are subtle discrepancies between the tests and the issue text, such as the tests relying on a new function, variable name, or error message that were introduced in the Gold Patch but is not mentioned or differs from the Issue Description.»
