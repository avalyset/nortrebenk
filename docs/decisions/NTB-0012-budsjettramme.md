# NTB-0012: Budget framework

- Status: adopted 2026-11-16

## Context

The study is to have no expenses beyond prepaid credit that existed on 16.11.2026. NTB-0007 planned three arms, where arm 3 (Codex) was to be charged to the OpenAI API.

## Decision

The study is carried out on prepaid credit that existed on 16.11.2026, with no top-up and no other expenses. The Codex arm (arm 3 in NTB-0007) is dropped from v1.0. The pilot measurement has two arms: Claude Code with Opus 5.5 and Claude Code with Sonnet 5.5. The number of runs per arm and task is set in the prereg from the cost measured in P2.4, and runs are cut before an arm is cut. v1.0 thus measures one vendor, and this is stated as a limitation in the README.

## Alternatives considered

- Top up credit to keep the Codex arm. Argument against the decision: two vendors strengthen independence. Rejected because the study is not to have expenses beyond existing credit; the idea is listed in IDEER.md.

## Consequences

v1.0 measures one vendor (Anthropic). The number of runs per arm and task is fixed in the prereg.

## Sources

- No external source; the decision was made by the author on 16.11.2026.
