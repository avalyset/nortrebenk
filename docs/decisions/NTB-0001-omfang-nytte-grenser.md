# NTB-0001: Scope, utility and limits

- Status: adopted 2026-11-16

## Context

The run validation (P1) ended on 16.11.2026: 21 of 30 candidates were validated on 5 repos, from two agencies (Nav 13, Digdir/Altinn 8), with repo language Kotlin 13 and TypeScript 8. The validated PRs were merged between 02.11.2026 and 14.11.2026. The task text (the PR description) was English in 13, Norwegian in 5 and mixed in 3.

## Decision

The purpose was set as measuring how well and how fast coding agents solve tasks from public code in Norwegian agencies, and what each solved task costs, with the agency's own tests as the ground truth. The users are technology leadership in the agencies (model class under a cost cap), DFD/Digdir/DFØ (benefit measurement without self-reporting) and researchers on developer productivity. v1.0 was defined as a task set, a repeatable method and a preregistered pilot measurement. It was decided that v1.0 is not a ranking of agents, not a picture of the agencies' code, not a measure of license value, not a measurement of human with agent and not a measurement of GitHub Copilot. «First Norwegian» is not used as the main claim.

## Alternatives considered

- Broader scope (more agencies, all languages, class B repos). Argument against the decision: a broader set would give better coverage of the agencies' code. Rejected because runnability has only been shown for the 21 tasks, and because more repos require services or tokens (see IDEER.md).
- «First Norwegian benchmark» as the main claim. Argument against the decision: the claim is easy to communicate. Rejected because earlier work exists in neighboring fields (see Sources), and because a first-of-its-kind claim cannot be fully verified.

## Consequences

The results apply only to the tasks in the set. Coverage is two agencies, five repos and two repo languages. Related work is mentioned in README and the datasheet: activity measurement of Copilot in Nav IT, a British trial of coding assistants in the public sector, non-English task text at repo level and Multi-SWE-bench, which has an Altinn repo (Altinn/app-frontend-react).

## Sources

- Stray et al., «Developer Productivity With and Without GitHub Copilot: A Longitudinal Mixed-Methods Case Study», arXiv:2509.20353: «We conducted a mixed-methods case study in NAV IT, a large public sector agile organization.»
- Government Digital Service, «AI coding assistant trial», gov.uk, published 12.09.2025: «The trial aimed to understand how these tools could help public sector engineering and development teams work better and be more productive.»
- «RuBench: A Repository-Level Agentic Coding Benchmark with Natively Authored Russian Task Specifications», arXiv:2607.06411: «each specified natively in Russian -- written from scratch, not translated»
- «Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving», arXiv:2504.02605: «we introduce a multilingual issue-resolving benchmark, called Multi-SWE-bench, covering Java, TypeScript, JavaScript, Go, Rust, C, and C++»
