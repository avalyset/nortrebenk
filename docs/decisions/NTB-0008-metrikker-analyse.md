# NTB-0008: Metrics and analysis

- Status: adopted 2026-11-16
- Changed 2026-11-16: primary outcome and pairwise comparison of text variants, see NTB-0013.

## Context

The tasks come from five repos, and tasks from the same repo are not independent. The set is small.

## Decision

Resolved means that all fail-to-pass and pass-to-pass tests pass. Resolved rate is reported per arm with an interval, both per task and clustered on repo (5 clusters). Cost per resolved task is the total cost of all runs, including failed ones, divided by the number resolved. Time is wall-clock from agent start to delivered patch, reported as median and quartiles. Differences between arms are reported pairwise per task with an interval, descriptively. No confirmatory hypothesis is formulated about which is best, and no comparison with human time spent is made. Text language and agent marker are reported as descriptive breakdowns.

## Alternatives considered

- Confirmatory test of the difference between arms. Argument against the decision: gives a clear conclusion. Rejected because the size of the set and the clustering give low power.
- Naive intervals only. Argument against the decision: simpler. Rejected because clustering on repo can give substantially wider intervals.

## Consequences

The intervals become wide with five clusters. The analysis code is locked in prereg-v1.

## Sources

- Miller, «Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations», arXiv:2411.00640: «Conceptualizing evaluation questions as having been drawn from an unseen super-population»; and from the PDF: «Analyzing the same data, clustered standard errors can be over 3X larger than naive standard errors.»
