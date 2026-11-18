# NTB-0011: Platform

- Status: adopted 2026-11-16
- Changed 2026-11-16: the cross-check is run through the unchanged Multi-SWE-bench harness.
- Changed 2026-11-18: the cross-check on amd64 was not run for v1.0 (AVVIK.md no. 12).

## Context

Validation and measurement are to take place on the same platform. P1 validated the tasks on linux/arm64. The Modal credit included for November did not cover agent runs.

## Decision

The measurement platform for the set and the pilot measurement is linux/arm64 locally, the same environment as P1. The trial on Modal that NTB-0002 described was not run. Before v1.0, the gold patch and the empty patch are run for all tasks in the set once on linux/amd64 as a cross-check, only if this can be done on included credit. Tasks that do not give the same outcome there are marked in the dataset and in the README, and the measurement results are not changed. NTB-0002 otherwise stands.

The cross-check on amd64 is run through the unchanged Multi-SWE-bench harness (24f493f), so that it also shows whether our runner gives the same fail-to-pass and pass-to-pass lists as the established harness. If that is not possible, it is run with our own runner, and this is recorded as a limitation.

## Alternatives considered

- Everything on amd64 on Modal. Argument against the decision: easier for others to reproduce. Rejected because validation and measurement are to take place on the same platform, and because the Modal credit included for November did not cover agent runs.
- Paid Modal use. Rejected, see NTB-0012.

## Consequences

The set is built and measured on linux/arm64. The README states the platform. The cross-check on amd64 is done only if included credit covers it.

## Sources

- No external source; the decision rests on the P1 protocol and NTB-0002.
