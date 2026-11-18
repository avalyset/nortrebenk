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

The runner was to be anchored against the published test lists for Altinn/app-frontend-react in Multi-SWE-bench. The dataset (ByteDance-Seed/Multi-SWE-bench) has no instances for the repo, and neither do Multi-SWE-RL, Multi-SWE-bench_mini or Multi-SWE-bench-flash. The comparison could not be made. See `data/anker/msb_altinn.md`. The runner is instead checked against the unchanged Multi-SWE-bench harness in the cross-check on amd64 in P4, if included credit covers it (NTB-0011).

## 6. The smoke trial search built under the disk limit (2026-11-16)

The limit for P2.4 was at least 6 GiB free on the disk before each build. The search for a smoke trial task in navikt/mock-oauth2-server (C1) started the build with 5 GiB free, because the search script did not measure the disk before each build. The build and the runs gave no disk error. Later builds were measured in advance and stopped under the limit.

## 7. New step P2.3b and two text variants (2026-11-16)

The map did not have the step. It was added after P2.3 let 4 of 21 tasks pass. The quality requirement now applies to extended text, and P3 runs two text variants (NTB-0013). The change was made before any agent run on the tasks in the set.

## 8. Dress rehearsal of the P3 runner before the freeze (2026-11-17)

The map did not have the step. A reading of the runner against the preregistration text found rules that were not implemented (the cap rule, the cost of a run stopped by the time cap, the budget check before reruns, the threshold for a pass with extended text only, the disk gate) and no way to continue after a stop. The runner was corrected (NTB-0014, changed 2026-11-17). It was then run end to end on the two smoke-test tasks outside the set, with the PR text only and one pass, and the budget cap and the time cap were each provoked once on one of them (`data/roykprove/generalprove.jsonl`). One correction from the freeze reading was made after the rehearsal: the task's instance image is kept when the disk gate cleans up between the two builds. It was checked without model calls on one of the tasks outside the set. No agent was run on a task in the set.

## 9. Four runs recorded as missing in pass 3 were run afterwards (2026-11-18)

In pass 3 the runner's free-space gate stopped two tasks before the build, and their four runs with extended text were recorded as missing, as the preregistration says (question 6). The gate measured once, right after cleanup. The measurement for the next task, taken within a few seconds, was above the limit, so the freed space had not yet been returned when the gate measured. The registered run files were first copied, hashed and timestamped. The four runs were then made with the same preparation function, caps and order, and written to a separate file (`data/p3/p3_tillegg.jsonl`); the gate passed at the first measurement for both tasks. The registered analysis is reported unchanged, with the four runs missing. A supplementary table includes them and is labelled as a deviation.

## 10. Operational watchdog during P3 (2026-11-17)

A separate script outside the repository watched the run file during P3. It would have stopped the runner if the last eight runs with an outcome were all missing, or if two completed runs in a row had hit the time cap. It was started at 11:29 UTC, after the runner (11:11 UTC), and never intervened. The registered runner code was not changed.

## 11. Descriptive additions and published run files (2026-11-18)

`analysis/lag_resultater.py` formats the tables in RESULTATER.md from the output of the locked analysis and from the run files, and adds no statistic. Two descriptive items were not pre-specified and are labelled so in RESULTATER.md: cost in NOK at the Norges Bank rate for 17 November 2026, and a per-task table of solved runs. The published run files are the registered files without the field `resultat_tekst` (the first 500 characters of the agent's final message). The locked analysis does not read that field and gives the same output with and without it.

## 12. Scope of the v1.0 freeze reduced (2026-11-18)

The cross-check on linux/amd64 through the unchanged Multi-SWE-bench harness (NTB-0011) was not attempted: no amd64 environment was set up for the pilot. The outcomes of the gold patch and the empty patch are therefore shown on linux/arm64 only, and the runner has not been compared with the unchanged Multi-SWE-bench harness. The cross-check is listed in IDEER.md. v1.0 is assessed against the Agentic Benchmark Checklist only; BetterBench and the JOSS checklist (NTB-0009) are not used, to keep the freeze of a pilot to the checklist written for agentic benchmarks.
