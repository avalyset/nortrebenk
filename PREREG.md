# Preregistration: nortrebenk v1.0 pilot measurement (P3)

**Status: frozen at git tag `prereg-v1`.** The deposit's DOI is recorded in `PREREG_DOI.txt` after publication (section «Registration sequence»).

Every number below was read from the file named next to it. Decision values (caps, seeds, budget rules) come from the decision records and are coded in `harness/agent/kjor_p3.py` and `harness/agent/kjor_agent.py`.

## Purpose

nortrebenk measures how well and how fast coding agents solve tasks taken from public code in Norwegian public agencies, and what each solved task costs. The agencies' own tests are the ground truth (NTB-0001). v1.0 is a task set, a repeatable method and a preregistered pilot measurement. It is not a ranking of agents, not a picture of the agencies' code, not a measure of licence value, not a measurement of a human working with an agent, and not a measurement of GitHub Copilot (NTB-0001). v1.0 measures one vendor, Anthropic (NTB-0012).

## AsPredicted questions

### 1. Have any data been collected for this study already?

No agent has been run on any task in the set. The following was seen before registration (details in «What has been seen before registration»): the outcomes of the gold patch and the empty patch in validation (P1, P2.2, P2.4) and in the grading-path check; quality ratings of both text variants by language models; four agent runs on two tasks outside the set; and a dress rehearsal of the P3 runner on the same two tasks. The P3 runner (`harness/agent/kjor_p3.py`) refuses to start agent runs on set tasks until `PREREG_DOI.txt` exists in the repository (NTB-0014).

### 2. What is the main question being asked or hypothesis being tested?

The study is descriptive. It has no confirmatory hypothesis about which arm is better, and no hypothesis tests are run (NTB-0008). The main measure is the solved share on the extended task text, per arm (NTB-0013). The secondary measures are all descriptive: solved share on the PR text alone, cost per solved task, wall time, and paired differences between arms and between text variants.

### 3. Describe the key dependent variable(s) specifying how they will be measured.

- **Solved** (per run): all fail-to-pass and pass-to-pass tests of the task pass when the agent's patch and the test patch are applied to the base commit in a fresh container without network (NTB-0008, `harness/agent/kjor_agent.py`, `vurder`). Changes to files the test patch touches are discarded before grading.
- **Cost** (per run): `total_cost_usd` as reported by Claude Code. Cost per solved task = total cost of all completed runs in an arm and text variant, divided by the number of solved runs (NTB-0008).
- **Wall time** (per run): from agent start to delivered patch, reported as median and quartiles.

### 4. How many and which conditions will participants be assigned to?

Within-task design with 2 arms × 2 text variants:

- Arms (NTB-0007, NTB-0012): Claude Code 2.1.325 with `claude-sonnet-5-5` and with `claude-opus-5-5` (source: `harness/agent/agentbilde.py`, `harness/agent/kjor_p3.py`).
- Text variants (NTB-0013): «PR text» (title and description as in `data/instances.jsonl`) and «extended» (the PR text followed by requirements and an interface, `data/utvidet_tekst.jsonl`).

### 5. Specify exactly which analyses you will conduct to examine the main question/hypothesis.

`analysis/analyse.py` (sha256 `3f75585107fd968738757c157341a22e178125dfcf383e3c3e3ba6bd82120968`), locked at the freeze and run with `--pass` on the runner's pass file. Standard errors follow Miller, arXiv:2411.00640 (NTB-0008):

- task score s_i = mean of the task's completed runs (Miller §3.1);
- a task with no completed runs in an arm and text variant is left out of the mean for that arm and text variant, and the number of such tasks is reported;
- solved share = mean of s_i over tasks; standard error by equation (1); 95 % interval by equation (3); clustered standard error with cluster = repository by equation (4) as printed, with n − 1 in the first term (Miller's appendix A has n);
- paired differences per task, Opus minus Sonnet within each text variant and extended minus PR text within each arm, with standard errors by equations (7) and (8), labelled descriptive; differences between the text variants are computed only from passes that have both variants;
- cost per solved task, and wall time as median and quartiles, per arm and text variant; when no run is solved, cost per solved task is not reported and the total cost is reported instead;
- the same numbers broken down by the outcome of the P2.3 quality check of the PR text, by the flag from the independent check, by repository, by text language and by agent marker; and the main measure with and without flagged tasks;
- missing runs, discarded attempts and incomplete passes, reported separately.

Only completed passes enter the main analysis (NTB-0014). With five repositories there are five clusters. Clustered standard errors from so few clusters are uncertain, and the output says so.

### 6. Describe exactly how outliers will be defined and handled, and your precise rule(s) for excluding observations.

No task is excluded after registration. Rules from NTB-0014:

- A run that hits a cap (the per-run budget or 40 minutes) counts as not solved, whatever the tests give; its cost and time count. If the time cap stops a run before Claude Code has reported a cost, the run's budget cap is recorded as its cost and the run is flagged in the run file.
- An infrastructure failure is a run that has hit no cap and where Claude Code exits with an API error or an execution error (result subtype `error_during_execution`), or where the container stops without a result line, or where the runner itself fails with an error before the run is recorded. Such a run is discarded and rerun, at most 2 times. If it fails a third time, it is recorded as missing and does not count as not solved.
- If the build, the self-test or the grading-path check for a task fails after two attempts, all the task's runs in that pass are recorded as missing. If fewer than 6 GiB are free on the Docker disk after cleanup, the build is not started and the task's runs in that pass are recorded as missing. If the self-test fails twice immediately before a run, that run and the task's remaining runs in that pass are recorded as missing.
- A pass is completed when every planned run has been done or is recorded as missing under these rules. A pass stopped by the budget is incomplete and is reported separately. If the runner stops for a reason outside these rules, it is restarted and continues with the planned runs that have no recorded outcome; the stop is reported.
- Discarded attempts, missing runs and their cost are reported.

### 7. How many observations will be collected or what will determine sample size?

The set has 21 tasks (source: `data/sett_v1.jsonl`). One pass is one run per task, arm and text variant: 84 runs. There are up to 3 passes; the plan `data/p3_plan.jsonl` has 252 runs (sha256 `1d83c17f1c2d20e48906e1c65fee454f52565e4d74f3121ac7cc3ca2a0249905`). The budget rules in NTB-0014 decide how many passes are run (section «Run plan and budget»).

### 8. Anything else you would like to pre-register?

See the full analysis plan below.

## Full analysis plan

### Task set (NTB-0003, NTB-0013)

`data/sett_v1.jsonl`: 21 tasks, sha256 `f5921aa0392ca99a75dc716cfc17f2bde86c7edbf35f4c44de8e3d4b29c2d5f7`, assembled by `harness/sett/lag_sett.py` from existing data files. Patches are in `data/instances.jsonl` (sha256 `f382ff9a02129e971d27565dede5776b78b182655084683b303005fa21f8d88c`).

- Repositories: navikt/mock-oauth2-server 5, Altinn/altinn-access-management-frontend 5, navikt/pensjonssimulator 4, navikt/kafka-manager 4, Altinn/altinn-support-dashboard 3.
- Code language (field `kodesprak`, the main language of the repository): Kotlin 13, TypeScript 8. The gold patch is in another language for some tasks: Altinn/altinn-support-dashboard #970 is C#, navikt/kafka-manager #329 is TypeScript, and navikt/kafka-manager #330 and #337 have both Kotlin and TypeScript (source: file names in the patches in `data/instances.jsonl`). Text language (field `tekstsprak`): engelsk (English) 13, norsk (Norwegian) 5, blandet (mixed) 3. Agent marker (field `agentmarkor`): nei (no) 18, ja (yes) 3.
- Merged between 2026-11-02T12:58:35Z and 2026-11-14T23:10:08Z; training-data cutoff for both models: claude-opus-5-5 Jun 2026, claude-sonnet-5-5 Jun 2026 (source: `data/modeller.json`).
- Platform: linux/arm64, local (NTB-0011). Wall time is an outcome measure, so the machine is stated: host MacBook Pro (MacBookPro18,3), Apple M1 Pro with 8 (6 Performance and 2 Efficiency) cores and 16 GB memory; Docker runs in a Colima VM with 4 CPUs and 8 GiB memory (source: `data/plattform.json`). Validation before inclusion: P1 status validert (validated) 21, krever_token (requires a registry token) 4, kjorefeil (run error) 2, ingen_gullpatch (no gold patch) 1, ingen_f2p (no fail-to-pass test) 1, regresjon (regression) 1 (source: `data/p1_resultater.jsonl`). In P2.2, all 21 tasks had B not solved and C solved 3/3 in a sealed image (source: `data/p22_resultater.jsonl`).
- Quality check of the PR text (P2.3; rule «at least 2 of 3», chosen on the human-annotated anchor with agreement 0.76, against 0.75 for «at least one»; source: `data/kvalitet/samsvar.md`): field `utfall_p23` utelukket (excluded) 17, består (passes) 4.
- Quality check of the extended text (P2.3b; source: `data/kvalitet/vurderinger_utvidet.jsonl`): the prompt and the rule were the same as in P2.3, and the OpenAI rater was to be called only where its vote could change the outcome, which applied to no task (NTB-0013); består 21.

### Text variants (NTB-0013)

The extended text is the PR text followed by «Requirements:» (one statement per item) and «Interface:» (type and name, location, inputs, outputs, description), following the format of SWE-Bench Pro. The additions were written in English by `claude-opus-5-5` from the PR text, gold patch, test patch and fail-to-pass names, using a fixed prompt (`harness/tekst/prompt_tillegg.txt`). They were then checked mechanically: no code blocks; no line equal to an added gold-patch line of at least 20 characters; every name in the interface present in the test patch or gold patch; every file path present in the gold patch; no @-handles or e-mail addresses. Outcome (source: `data/utvidet_tekst.jsonl`): 20 approved on the first attempt, 1 on the second, 0 failed.

### Arms, sealing and prompt (NTB-0006, NTB-0007)

- Claude Code 2.1.325, installed as a standalone binary checked against the release manifest's sha256 (`harness/agent/agentbilde.py`). Models `claude-sonnet-5-5` and `claude-opus-5-5`; default settings except what sealing requires; the environment switches are in `MILJØ` in `harness/agent/agentbilde.py`.
- Flags: `claude -p`, `--output-format stream-json --verbose`, `--dangerously-skip-permissions`, `--disallowedTools WebSearch WebFetch`, `--max-budget-usd` 1.50 (Sonnet) and 3.00 (Opus); time limit 40 minutes in the runner (source: `harness/agent/kjor_p3.py`, `harness/agent/kjor_agent.py`).
- Sealing: the agent container sits on an internal Docker network with no route out. The only way out is a proxy that forwards paths under `/v1/` to the model API, adds the API key and rejects server-side web search and web fetch tools. Package registries and github.com are unreachable. The agent image contains no gold patch, test patch or run scripts; the repository has one commit, no remotes and one ref. A self-test checks this before every run (`harness/agent/selvtest.sh`): it tries to reach github.com, registry.npmjs.org and repo.maven.apache.org, and it checks that up to three of the longest added gold-patch lines (at least 30 characters and not already in the base commit) are not found under `/home`, `/root` or `/tmp`.
- For the two kafka-manager tasks with build fields in `data/sett_v1.jsonl`, dependency caches from the gold-patch state are added in a build stage that keeps only the caches (`harness/agent/gullcache.py`). P2.4 showed that their tests then run without network (https://github.com/navikt/kafka-manager/pull/330: B solved False, C solved 3/3 without network; https://github.com/navikt/kafka-manager/pull/336: B solved False, C solved 3/3 without network; source: `data/p24_nett.jsonl`).
- Wrapper, verbatim (`harness/agent/innpakning.txt`), identical for all tasks, arms and text variants:

```
You are working in a git repository checked out at {sti}. Below is the title and description of a change request for this repository. Make the code changes needed to fulfil it. Do not change or add test files; tests for the change will be applied and run after you finish. Stop when the change is complete.

Title: {tittel}

Description:
{beskrivelse}
```

### Run plan and budget (NTB-0014)

- Up to 3 passes of 84 runs; a pass with extended text only has 42 runs, two per task. Task order within a pass is shuffled with seed 20261116 + pass number, and the order of a task's four runs follows the same seed. Per task: build instance and agent image, self-test, grading-path check without model calls (gold patch without test files gives solved, empty patch gives not solved), the four runs one at a time, delete the images.
- Budget B = Anthropic balance read just before P3 minus 5.00 USD. Spent = sum over all runs, discarded attempts included. The first pass starts only if B ≥ 28.29 USD. A new full pass starts only if what remains of B is at least 1.5 × the cost of the most expensive completed pass. Otherwise an extended-text-only pass is run if what remains is at least 1.5 × the cost of the extended part of the most expensive pass. Otherwise P3 stops. No run starts if spent plus the run's cap would exceed B.
- Plan: `data/p3_plan.jsonl`, 252 runs, sha256 `1d83c17f1c2d20e48906e1c65fee454f52565e4d74f3121ac7cc3ca2a0249905`.

### What has been seen before registration

- Gold patch and empty patch: P1 validation (source: `data/p1_resultater.jsonl`); P2.2 stability over three runs (source: `data/p22_resultater.jsonl`); P2.4 network-free runs for kafka-manager #330 and #336 (source: `data/p24_nett.jsonl`).
- Grading-path check before the freeze, without model calls, for 6 tasks (source: `data/p3_kontroll.jsonl`): passed 6 (navikt__kafka-manager__330, navikt__mock-oauth2-server__1069, navikt__pensjonssimulator__688, Altinn__altinn-support-dashboard__966, Altinn__altinn-access-management-frontend__2619, navikt__kafka-manager__336); failed 0. The checks were run with the runner as it was before the corrections of 2026-11-17 (AVVIK.md no. 8); for the first three tasks listed, the self-test did not yet skip lines that occur in the base commit. Each check covered build, self-test, gold patch without test files giving solved, and empty patch giving not solved. Earlier attempts are recorded in the same file: Altinn__altinn-support-dashboard__966 failed at selvtest (self-test); Altinn__altinn-access-management-frontend__2619 failed at selvtest; navikt__kafka-manager__336 was not started twice, with less than 6 GiB free after cleanup (4.9 GiB, then 5.9 GiB). The self-test failures came from gold-patch lines that already occur in the base commit; the self-test now skips such lines and checks up to three of the longest remaining ones (`harness/agent/selvtest.sh`).
- Quality ratings of the PR text (P2.3; `data/kvalitet/vurderinger.jsonl`, 63 lines) and of the extended text (P2.3b; `data/kvalitet/vurderinger_utvidet.jsonl`, 63 lines), by `claude-sonnet-5-5`, `gpt-6.1-sol` (P2.3 only; not called in P2.3b) and `gemini-3.5-flash-lite`.
- The OpenAI rater (gpt-6.1-sol) assessed the extended text for 21 tasks and voted for exclusion for 0 (source: `data/kvalitet/uavhengig_utvidet.jsonl`). Flagged tasks stay in the set (the rule needs two votes), and the main measure is reported with and without them (NTB-0013).
- Four agent runs on two tasks outside the set (source: `data/roykprove/kjoringer.jsonl`):
  - https://github.com/Altinn/altinn-access-management-frontend/pull/2552, claude-opus-5-5: solved yes, 0.1678 USD, 9 turns, 41.5 s
  - https://github.com/Altinn/altinn-access-management-frontend/pull/2552, claude-sonnet-5-5: solved no, 0.0405 USD, 4 turns, 10.8 s
  - https://github.com/navikt/mock-oauth2-server/pull/1105, claude-opus-5-5: solved yes, 0.3492 USD, 17 turns, 109.9 s
  - https://github.com/navikt/mock-oauth2-server/pull/1105, claude-sonnet-5-5: solved yes, 0.0998 USD, 8 turns, 59.3 s
- A dress rehearsal of the P3 runner on the same two tasks outside the set, with the PR text only: the budget cap and the time cap were each provoked once, and the runner was then run end to end for one pass (source: `data/roykprove/generalprove.jsonl`; AVVIK.md no. 8):
  - https://github.com/navikt/mock-oauth2-server/pull/1105, claude-sonnet-5-5: solved no, 0.0441 USD, 1 turn, 5.0 s (budget cap 0.02 USD provoked)
  - https://github.com/navikt/mock-oauth2-server/pull/1105, claude-sonnet-5-5: solved no, 1.5000 USD, no result line, 25.8 s (time cap 25 s provoked); cost set to the cap
  - https://github.com/navikt/mock-oauth2-server/pull/1105, claude-opus-5-5: solved yes, 0.3384 USD, 14 turns, 110.9 s
  - https://github.com/navikt/mock-oauth2-server/pull/1105, claude-sonnet-5-5: solved yes, 0.1420 USD, 14 turns, 55.8 s
  - https://github.com/Altinn/altinn-access-management-frontend/pull/2552, claude-sonnet-5-5: solved no, 0.0385 USD, 4 turns, 8.1 s
  - https://github.com/Altinn/altinn-access-management-frontend/pull/2552, claude-opus-5-5: solved yes, 0.2054 USD, 7 turns, 35.1 s
- No agent has been run on any task in the set.
- Anchors made before the quality check and before the additions were written:
  - `FORANKRING_for-P2.3_20261116T125720Z.txt` (written 2026-11-16T12:57:20Z; OpenTimestamps: confirmed in Bitcoin blocks 976131 and 976134; source: `ots info` on the proof in the author's internal repository).
  - `FORANKRING_for-P2.3b_20261116T151046Z.txt` (written 2026-11-16T15:10:46Z; OpenTimestamps: confirmed in Bitcoin blocks 976145, 976146 and 976167; source: `ots info` on the proof in the author's internal repository).

### Decision records made before registration

NTB-0001 to NTB-0014 in `docs/decisions/`. Changes made after the outcome of P2.3 was known are recorded in AVVIK.md (no. 7 and no. 8), NTB-0013, NTB-0014 and the change lines in NTB-0003, NTB-0004, NTB-0007, NTB-0008 and NTB-0011.

### Limits

- v1.0 is not a ranking of agents, not a picture of the agencies' code, not a measure of licence value, not a measurement of a human with an agent and not a measurement of GitHub Copilot (NTB-0001). It measures one vendor (NTB-0012).
- The quality-check anchor consists of English-language Python tasks the models may have seen in training, including the outcome of the annotation. The set is Kotlin, TypeScript and C# with Norwegian and English text (NTB-0004). The Google rater was a free-tier model (AVVIK.md no. 4).
- The agent setup is not anchored to published solve rates (NTB-0007).
- Platform linux/arm64. A cross-check on amd64 through the unmodified Multi-SWE-bench harness is run only if included credit covers it (NTB-0011). The runner anchor against Multi-SWE-bench fell away (AVVIK.md no. 5).
- The extended text was added after the outcome of P2.3 and the smoke test were known, and before any agent run on set tasks. The additions were written by a model from the same vendor as the agents, without human review; a task's pass may rest on the rater from the same vendor; and the additions state names and strings from the solution (NTB-0013).
- The smoke test built once below the disk limit (AVVIK.md no. 6).
- Claude Code can exceed the per-run budget cap: in the rehearsal a cap of 0.02 USD gave a cost of 0.0441 USD (source: `data/roykprove/generalprove.jsonl`).
- Cost that Claude Code has not reported is not counted as spent: a run that is interrupted when the runner stops, and an attempt discarded because the runner itself failed. B leaves 5.00 USD of the balance unused (NTB-0014).
- For the two kafka-manager tasks with build fields, the dependency caches come from the gold-patch state and show which dependencies the solution uses (`harness/agent/gullcache.py`).
- Sample: 21 tasks from 5 repositories in two GitHub organisations, navikt and Altinn, merged between 2026-11-02T12:58:35Z and 2026-11-14T23:10:08Z (source: `data/sett_v1.jsonl`).
- Validation was done with an own runner on linux/arm64, not through unmodified Multi-SWE-bench (AVVIK.md no. 1).

### Registration sequence

1. The author approves this document; the freeze is a separate step after approval.
2. Signed git tag `prereg-v1`.
3. `git archive` of the tag → `nortrebenk_prereg-v1_<date>.tar.gz`.
4. OpenTimestamps: `ots stamp` on the tarball and on `PREREG.md`.
5. Zenodo deposit of the tarball, `PREREG.md` and both `.ots` proofs.
6. Publication gives the DOI → `PREREG_DOI.txt` → signed commit.
7. The P3 runner's guard opens once `PREREG_DOI.txt` exists; no agent run on a set task before the signed commit of step 6.

### Deviations

Deviations after registration are recorded in AVVIK.md with date and reason, and reported with the results.

## References

- Xiang Deng, Jeff Da, Edwin Pan and others, «SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?», arXiv:2509.16941.
- Evan Miller, «Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations», arXiv:2411.00640.
- Sayash Kapoor, Benedikt Stroebl, Zachary S. Siegel, Nitya Nadgir, Arvind Narayanan, «AI Agents That Matter», arXiv:2407.01502.
