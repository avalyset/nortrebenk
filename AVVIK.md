# Deviations

Deviations from the plan are recorded here with date and justification. Decisions made before the preregistration are recorded as ADRs in `docs/decisions/` and are not deviations.

## 1. P1 run on linux/arm64 with own thin runner (2026-11-16)

The run validation in P1 was run on linux/arm64 with an own thin runner built on the Multi-SWE-bench classes, not through unchanged Multi-SWE-bench. Multi-SWE-bench's run goes via an image that exists only for linux/amd64. See NTB-0002.

## 2. Rule for run errors added during P1 (2026-11-16)

The rule «C without test reports gives kjorefeil» (C = base + test patch + gold patch) was added during P1, after the first repo. One candidate was reclassified from «ingen_f2p» to «kjorefeil» based on the stored logs, without a new run. The rule did not change the number validated.

## 3. The Codex arm was dropped (2026-11-16)

The Codex arm, which was in the original plan, was dropped from v1.0 because the study is carried out without expenses beyond existing credit (NTB-0012).

## 4. Google rater on free tier only (2026-11-16)

NTB-0004 requires one rater from Google. The Gemini key's project is on the free tier (Google AI Studio, 16.11.2026), and the study is not to have expenses beyond existing credit (NTB-0012). The strongest free model with a daily quota for all 121 calls, gemini-3.5-flash-lite, was used. It is not the vendor's strongest model.

## 5. The runner anchor against Multi-SWE-bench was dropped (2026-11-16)

The runner was to be anchored against the published test lists for Altinn/app-frontend-react in Multi-SWE-bench. The dataset (ByteDance-Seed/Multi-SWE-bench) has no instances for the repo, and neither do Multi-SWE-RL, Multi-SWE-bench_mini or Multi-SWE-bench-flash. The comparison could not be made. See `data/anker/msb_altinn.md`. The runner is instead checked against the unchanged Multi-SWE-bench harness in the cross-check on amd64 in P4 (NTB-0011).

## 6. The smoke trial search built under the disk limit (2026-11-16)

The limit for P2.4 was at least 6 GiB free on the disk before each build. The search for a smoke trial task in navikt/mock-oauth2-server (C1) started the build with 5 GiB free, because the search script did not measure the disk before each build. The build and the runs gave no disk error. Later builds were measured in advance and stopped under the limit.

## 7. New step P2.3b and two text variants (2026-11-16)

The map did not have the step. It was added after P2.3 let 4 of 21 tasks pass. The quality requirement now applies to extended text, and P3 runs two text variants (NTB-0013). The change was made before any agent run on the tasks in the set.
