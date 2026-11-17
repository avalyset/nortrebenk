# PLAN – nortrebenk

**Purpose:** measure how well and how fast coding agents solve tasks from public code in Norwegian agencies, and what each resolved task costs. The ground truth is the agency's own tests.

**Users:** technology leadership in the agencies (model class under a cost cap), DFD/Digdir/DFØ (benefit measurement without self-reporting), researchers on developer productivity.

**Start:** P1, whether the tasks can be run. **Middle:** prereg-v1, everything locked before agent data. **End:** v1.0 with DOI. The map ends there.

## Map (fixed order; deviations are recorded in AVVIK.md)

- P0 Recon and frozen candidate list
- P1 Run validation (fail-to-pass)
- P2 Repo, set and preregistration
  - P2.1 Repo and ADR
  - P2.2 Set building locally on linux/arm64: sealing, stability over three runs, empty-patch check, dedup, training cutoffs
  - P2.3 Quality check of the tasks
  - P2.3b Extended task text with requirements and interface, and a new quality check of it (NTB-0013)
  - P2.4 Anchor and smoke trial on tasks outside the set; budget cap
  - P2.5 Preregistration (prereg-v1), with translation of the repo's documents to English and a dress rehearsal of the runner (AVVIK.md no. 8)
- P3 Pilot run under the preregistration: Claude Code with Opus 5.5 and with Sonnet 5.5, on extended text and on the PR text alone
- P4 Freeze of v1.0, with cross-check on amd64 before the freeze if included credit covers it

The status of each phase is in the ground truth, not here.

## Decisions (ADR)

- [NTB-0001: Scope, utility and limits](docs/decisions/NTB-0001-omfang-nytte-grenser.md)
- [NTB-0002: Format, platform and runner](docs/decisions/NTB-0002-format-plattform-kjorer.md)
- [NTB-0003: Inclusion in the set](docs/decisions/NTB-0003-inklusjon.md)
- [NTB-0004: Quality check](docs/decisions/NTB-0004-kvalitetssjekk.md)
- [NTB-0005: Agent traces](docs/decisions/NTB-0005-agentspor.md)
- [NTB-0006: Sealing](docs/decisions/NTB-0006-forsegling.md)
- [NTB-0007: Agents, models and payment](docs/decisions/NTB-0007-agenter-modeller-betaling.md)
- [NTB-0008: Metrics and analysis](docs/decisions/NTB-0008-metrikker-analyse.md)
- [NTB-0009: Publication, maintenance and retirement](docs/decisions/NTB-0009-publisering-vedlikehold-pensjonering.md)
- [NTB-0010: Personal data](docs/decisions/NTB-0010-personopplysninger.md)
- [NTB-0011: Platform](docs/decisions/NTB-0011-plattform.md)
- [NTB-0012: Budget framework](docs/decisions/NTB-0012-budsjettramme.md)
- [NTB-0013: Text variants](docs/decisions/NTB-0013-tekstvarianter.md)
- [NTB-0014: Run plan for P3](docs/decisions/NTB-0014-kjoreplan-p3.md)
