# NTB-0003: Inclusion in the set

- Status: adopted 2026-11-16
- Changed 2026-11-16: the quality requirement applies to extended task text, see NTB-0013.

## Context

P1 validated 21 of 30 candidates. Validation in P1 meant at least one fail-to-pass test and no test that passed on base and failed with the gold patch, in one run on linux/arm64.

## Decision

A task is admitted to the set when all of the following are met: it is P1-validated; it has a stable fail-to-pass set over three runs on the platform from NTB-0002; it builds without a token; the license is MIT or Apache-2.0; it was merged after the latest training cutoff among the models being measured; it is not in Multi-SWE-bench or SWE-rebench V2; and it passes the quality check (NTB-0004). The base is base_sha as it was validated. Candidates that were not validated in P1 are not admitted. The number that remains is a result. If fewer than 20 remain, v1.0 is published as a method and feasibility findings without lowering the requirements.

## Alternatives considered

- Admit non-validated candidates after manual repair (e.g. merge parent as base). Argument against the decision: more tasks. Rejected because repairs after the result is known make the selection depend on the outcome; the idea is in IDEER.md.
- Lower the requirements if fewer than 20 remain. Argument against the decision: the set would have been larger. Rejected because the requirements would then have been set after the data.

## Consequences

The size of the set is unknown until P2.2–P2.3 are done. The training cutoffs for all models must be fixed before inclusion.

## Sources

- «SWE-rebench: An Automated Pipeline for Task Collection and Decontaminated Evaluation of Software Engineering Agents», arXiv:2505.20411: «show that performance of some language models might be inflated due to contamination issues»
