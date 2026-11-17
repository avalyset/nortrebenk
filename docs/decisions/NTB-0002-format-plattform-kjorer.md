# NTB-0002: Format, platform and runner

- Status: adopted 2026-11-16
- The platform item is superseded by NTB-0011.

## Context

In P1 the instances were written as Multi-SWE-bench definitions against commit 24f493f and run with a thin runner built on the Multi-SWE-bench classes. Multi-SWE-bench's own run used an image that only existed for linux/amd64, while the machine ran linux/arm64. P1 therefore validated on linux/arm64.

## Decision

The instances are written as Multi-SWE-bench definitions against commit 24f493f. The runner is the thin runner from P1, built on the Multi-SWE-bench classes. The platform for the set and the measurement is decided by one bounded trial in P2.2: kafka-manager (4 tasks) is built and run as linux/amd64 on Modal. If the trial gives the same fail-to-pass and pass-to-pass lists as P1, amd64 on Modal is the platform, and all tasks are validated there. Otherwise the platform is linux/arm64 locally, and the limitation is stated in README. The outcome is recorded in NTB-0011. In either case it is not claimed that the instances were run through unmodified Multi-SWE-bench.

## Alternatives considered

- Own harness and own format. Argument against the decision: full control and no dependency on an external codebase. Rejected because an established format makes the instances reusable.
- Unmodified Multi-SWE-bench on amd64 locally via emulation. Argument against the decision: it would have given a run through the unmodified harness. Rejected because JVM and Node builds under emulation were judged too slow, and because the colima configuration was not to be changed.
- All validation directly on Modal without a trial. Argument against the decision: saves one step. Rejected because a trial on one repo shows whether the platforms give the same test lists before all validation is moved.

## Consequences

P2.2 starts with the trial on kafka-manager. The platform choice is recorded in NTB-0011. harness/BRUK.md describes the runner as a thin runner on the Multi-SWE-bench classes.

## Sources

- The SWE-bench documentation, «Evaluation – SWE-bench», the section «Cloud-Based Evaluation» (swebench.com/SWE-bench/guides/evaluation/): «Run evaluation on Modal»
