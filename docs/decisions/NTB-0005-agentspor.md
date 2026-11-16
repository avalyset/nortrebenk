# NTB-0005: Agent traces

- Status: adopted 2026-11-16

## Context

The prior facts from P1 marked agent marker yes when PR text or commit messages had explicit traces (e.g. «Co-authored-by: Copilot» or «Generated with Claude Code»). 3 of the 21 validated tasks had a marker.

## Decision

Each task is marked with agent marker yes or no based on PR text and commit messages. The tasks are kept, and the result is also reported split by the marker. Absence of a marker does not mean the code is human-written.

## Alternatives considered

- Exclude tasks with a marker. Argument against the decision: tasks solved with an agent may be easier for agents. Rejected because the marker only captures explicit traces, so exclusion would have produced a false dividing line.

## Consequences

The report shows results for all tasks and split by marker. The marker describes only visible traces.

## Sources

- No external source; the decision rests on the prior facts from P1.
