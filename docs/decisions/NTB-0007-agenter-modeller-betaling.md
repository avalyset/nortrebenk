# NTB-0007: Agents, models and payment

- Status: adopted 2026-11-16
- Arm 3 is dropped from v1.0, see NTB-0012.
- Changed 2026-11-16 (2): wrapper, version and run order.
- Changed 2026-11-16 (3): two text variants in P3, see NTB-0013.
- Changed 2026-11-17: the number of runs and the caps follow NTB-0014 (up to three passes, a cap per run), and cost is `total_cost_usd` as reported by Claude Code.

## Context

The study is to report cost per solved task. The cost must be measured per call and be separate from subscriptions.

## Decision

Three arms are run in priority order: Claude Code with Opus 5.5, Claude Code with Sonnet 5.5, and Codex with the current top model (model ID fixed in P2.4, [U] until then). Three runs are made per arm and task. The Claude arms are run first and are charged to the Anthropic API, not the Max subscription, so that the cost can be measured; Codex is charged to the OpenAI API. If the budget cap does not suffice, runs are cut before arms, and arm 3 before arm 2. The agents are run with default settings and without their own prompt tuning. Time limit, cost cap per task and total budget cap are set from P2.4. No run is added to use up credit.

The agent receives the task's title and description in a fixed wrapper (harness/agent/innpakning.txt), the same for all tasks and arms. The Claude Code version is fixed and recorded. The runs go one at a time. The cap per run is set with the agent's own budget limit and a time limit in the runner. The only deviation from the default settings is what the sealing requires (NTB-0006). The agent setup is not anchored against published solve rates in v1.0, because the credit does not cover a sample large enough to compare rates.

## Alternatives considered

- GitHub Copilot as an arm. Argument against the decision: it is the tool the agencies pay for. Rejected in v1.0 because cost per call cannot be measured in the same way; the idea is in IDEER.md.
- One run per arm and task. Argument against the decision: lower cost. Rejected because variation between runs then cannot be estimated.

## Consequences

Cost is reported from the API billing. The arm order determines what is cut in case of budget shortage.

## Sources

- Kapoor et al., «AI Agents That Matter», arXiv:2407.01502: «Our focus on cost in addition to accuracy motivates the new goal of jointly optimizing the two metrics.»
