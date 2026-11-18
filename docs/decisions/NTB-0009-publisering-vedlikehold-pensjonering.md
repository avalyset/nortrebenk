# NTB-0009: Publication, maintenance and retirement

- Status: adopted 2026-11-16
- Changed 2026-11-18: v1.0 is assessed against the Agentic Benchmark Checklist only; BetterBench and the JOSS checklist are not used for the pilot (AVVIK.md no. 12).

## Context

The set consists of fresh tasks from public repos. It becomes contaminated when newer models are trained on data after the merge dates.

## Decision

Full instances are published with a canary string and a license statement per repo. v1.0 is corrected only for errors that change a number. The set is valid for models with a training cutoff before the earliest merge date in the final set; for newer models it is retired, and the date is stated in the README. The completion criteria at P4 are the Agentic Benchmark Checklist, BetterBench and the JOSS checklist. The datasheet is written following Datasheets for Datasets.

## Alternatives considered

- Continuous updating of v1.0. Argument against the decision: the set is kept fresh. Rejected because published numbers would then change; refills are listed in IDEER.md as v1.1.

## Consequences

The README gets a retirement date. The freeze at P4 is assessed against the three checklists.

## Sources

- «Establishing Best Practices for Building Rigorous Agentic Benchmarks» (Agentic Benchmark Checklist), arXiv:2507.02825: «we show that many agentic benchmarks have issues in task setup or reward design.»
- «BetterBench: Assessing AI Benchmarks, Uncovering Issues, and Establishing Best Practices», arXiv:2411.12990: «we develop an assessment framework considering 46 best practices across an AI benchmark's lifecycle»
- «Datasheets for Datasets», arXiv:1803.09010 (identifier checked against the title on the arXiv page): «we propose that every dataset be accompanied with a datasheet that documents its motivation, composition, collection process, recommended uses, and so on.»
- The JOSS checklist: not retrieved in P2.1.
