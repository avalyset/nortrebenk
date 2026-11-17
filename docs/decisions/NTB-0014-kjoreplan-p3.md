# NTB-0014: Run plan for P3

- Status: adopted 2026-11-16
- Changed 2026-11-17: clarifications before the freeze (cap rule, cost at the time cap, execution errors, disk gate, self-test before a run, budget check before reruns, restart).

## Context

P3 is to run the tasks in the set with two arms, two text variants and three runs (NTB-0007, NTB-0013). The disk cannot hold images for all the tasks at the same time, and the credit has a cap (NTB-0012). The smoke trial measured at most 9.43 USD for one round over 21 tasks and two arms. The grading path in the agent runner is a different code path from the validation in P2.2, and two tasks need a separate build to run the tests without network.

## Decision

P3 is run in up to three passes. One pass is one run per task, arm and text variant, that is, 84 runs for 21 tasks. Within a pass the tasks are taken in an order shuffled with seed 20261116 plus the pass number. For each task the instance image and the agent image are built, the self-test is run, the grading path is checked without model calls (the gold patch excluding test files gives resolved, the empty patch gives not resolved), the four runs are done in an order given by the same seed, and the images are deleted. The runs go one at a time. The plan with all the runs in order is made by the runner before the freeze and is in data/p3_plan.jsonl.

The cap per run is 1.50 USD for Sonnet 5.5 and 3.00 USD for Opus 5.5, set with the agent's budget limit, and 40 minutes. A run that hits a cap counts as not resolved, and cost and time are counted.

The budget B is the Anthropic balance read just before P3 minus 5.00 USD. Amount spent is the sum over all runs, including discarded attempts. The first pass is started only if B is at least 28.29 USD (1.5 times two rounds of 9.43 USD). A new full pass is started only if what remains of B is at least 1.5 times the cost of the most expensive completed pass. If it does not suffice for a full pass, a pass with extended text only is run if what remains is at least 1.5 times the cost of the extended part of the most expensive pass. Otherwise P3 stops. Within a pass no run is started if amount spent plus the run's cap exceeds B.

An infrastructure failure in a run is that Claude Code exits with an API error, or that the container stops without a result line and without a cap having been hit. The run is then discarded and run again, at most two times. If it fails the third time, it stands as missing and does not count as not resolved. If the build, the self-test or the check of the grading path fails for a task after two attempts, all the task's runs in the pass stand as missing. Discarded attempts, missing runs and the cost of them are reported.

A pass is completed when each planned run has either been carried out or stands as missing according to the rules above. A pass stopped by the budget is incomplete. Only completed passes are included in the main analysis, and incomplete ones are reported separately.

The runner for P3 refuses to run agents on tasks in the set before PREREG_DOI.txt exists in the repo.

Clarifications 2026-11-17, made before the freeze and before any agent run on the tasks in the set. A run that hits a cap is recorded as not resolved whatever the tests give. If the time cap stops a run before Claude Code has reported a cost, the run's budget cap is recorded as its cost and the run is flagged. An infrastructure failure also covers a run where Claude Code reports an execution error (result subtype error_during_execution) without a cap having been hit. If less than 6 GiB is free on the Docker disk after cleanup, the build is not started and the task's runs in the pass stand as missing. If the self-test fails twice immediately before a run, that run and the task's remaining runs in the pass stand as missing. The budget check is made before every attempt, reruns included. If the runner stops for a reason outside these rules, it is restarted and continues with the planned runs that have no recorded outcome; a run that was in progress is run again.

## Alternatives considered

- All twelve runs per task in one build. Argument against the decision: fewer builds. Rejected because a budget that runs out along the way would then give some tasks all runs and others none.
- Keep all the images throughout P3. Rejected because the disk cannot hold them.
- Check the grading path only before the freeze. Argument against the decision: shorter passes. Rejected because builds can change between freeze and run, and an error in the grading path would otherwise stand as not resolved.

## Consequences

P3 takes three passes with build and check for each task in each pass. The order is fixed and published before the first run.

## Sources

- data/roykprove/budsjett.md; no external source.
