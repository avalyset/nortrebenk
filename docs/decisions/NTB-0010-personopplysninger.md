# NTB-0010: Personal data

- Status: adopted 2026-11-16

## Context

The task texts are PR descriptions from public repos and may contain usernames and email addresses.

## Decision

The instances have no author field. @-usernames and email addresses are removed from the task text. The PR URL is kept as the source reference.

## Alternatives considered

- Keep an author field. Argument against the decision: full traceability to the person. Rejected because the PR URL gives traceability without the set storing personal data.

## Consequences

The cleaning is done mechanically when the set is built and checked before the freeze.

## Sources

- No external source.
