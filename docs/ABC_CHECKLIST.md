# Agentic Benchmark Checklist: nortrebenk v1.0

Assessment of v1.0 against the Agentic Benchmark Checklist (ABC) in «Establishing Best Practices for Building Rigorous Agentic Benchmarks», arXiv:2507.02825v5 (https://arxiv.org/html/2507.02825v5, retrieved 2026-11-18T06:17:31Z; the items are in figures 2–4 of that version). Each item is given with its ID and a short paraphrase. The answer is yes, partly or no, with one sentence and a file reference. Items for evaluation methods nortrebenk does not use are marked «not applicable»: nortrebenk grades code with unit tests (the agency's own tests), so of the outcome-validity groups only O.d (unit testing) applies. O.f.2 (non-deterministic test results) is answered as well, because it bears on any test-based grading; the rest of O.f (end-to-end testing) is not applicable. The item IDs follow figures 2–4; O.f.3, which occurs only in the paper's appendix tables, is not included. NTB-0009 and AVVIK.md no. 12 record that v1.0 is assessed against this checklist only.

## Task validity

| ID | Item (paraphrased) | Answer | Basis |
|---|---|---|---|
| T.1 | Tool versions are stated. | partly | The Claude Code version is fixed and checked against the release manifest, and each task's base image is recorded, but tool versions are not stated in the task prompt (`harness/agent/agentbilde.py`, field `base_image` in `data/instances.jsonl`, `harness/agent/innpakning.txt`). |
| T.2 | API tools needed by the task are reliably reachable during evaluation. | yes | The only external service is the model API, reached through one proxy; no run in P3 ended with an error (`harness/agent/mellomtjener.py`, RESULTATER.md table T3). |
| T.3 | Evaluation stops or handles errors properly if an API becomes unreachable. | yes | An API or execution error is an infrastructure failure that is discarded and rerun at most twice, then recorded as missing (NTB-0014, `harness/agent/kjor_p3.py`). |
| T.4 | Leftover data or state is cleared between runs. | yes | Each run starts a fresh container from the agent image, grading uses a fresh container, and the images are deleted after each task (PREREG.md, `harness/agent/kjor_agent.py`). |
| T.5 | The agent is fully isolated from ground-truth information. | partly | The agent image has no gold patch, test patch or run scripts, the repository has one commit, no remotes and one ref, the network has no route out except the model API, and a self-test checks this before every run; but for the two kafka-manager tasks with build fields, the dependency caches come from the gold-patch state and show which dependencies the solution uses (NTB-0006, `harness/agent/selvtest.sh`, `harness/agent/gullcache.py`). |
| T.6 | The setup does not change over time. | partly | Base commits, patches, base images (pinned by digest) and the Claude Code version are fixed, but the images are built for each pass with dependencies fetched at build time, and the model API is a live service (`data/instances.jsonl`, `harness/agent/agentbilde.py`). |
| T.7 | The ground truth is verified for correctness. | partly | The tests are validated mechanically (fail before, pass with the gold patch, stable over three runs), and the quality check by three model raters looks for tests that reject valid solutions; no human reviewed them (`data/p1_resultater.jsonl`, `data/p22_resultater.jsonl`, NTB-0004). |
| T.8 | Each task is verified to be solvable. | yes | The gold patch solved every task in 3 of 3 runs in a sealed image, and the grading path is checked per task before each pass (`data/p22_resultater.jsonl`, NTB-0014). |
| T.9 | The benchmark includes an oracle solver. | yes | The gold patch is the oracle; the grading-path check applies it without test files and requires solved (`harness/agent/kjor_agent.py`, `kontroll`). |
| T.10 | The implementation has no exploitable holes that pass evaluation without doing the task. | partly | Agent changes to files the test patch touches are discarded before grading, and the empty patch must give not solved, but no adversarial review of the harness was made (`harness/agent/kjor_agent.py`, RESULTATER.md table T3). |

## Outcome validity

| ID | Item (paraphrased) | Answer | Basis |
|---|---|---|---|
| O.a.1 | String matching accepts semantically equivalent expressions. | not applicable | No string matching; grading is by tests (NTB-0008). |
| O.a.2 | String matching handles redundant words. | not applicable | No string matching (NTB-0008). |
| O.b.1 | Substring matching handles negations. | not applicable | No substring matching (NTB-0008). |
| O.b.2 | Substring matching resists listing all possible answers. | not applicable | No substring matching (NTB-0008). |
| O.b.3 | The ground truth is complex enough to prevent guessing. | not applicable | The item belongs to substring matching; the empty patch is checked to give not solved for every task (NTB-0014). |
| O.c.1 | The LLM judge's accuracy and consistency are documented. | not applicable | No LLM judge grades the agent runs; model raters were used only in the quality check, measured against human annotations (`data/kvalitet/samsvar.md`). |
| O.c.2 | The LLM judge resists adversarial inputs. | not applicable | No LLM judge grades the agent runs (NTB-0008). |
| O.d.1 | Test cases are verified for correctness and quality. | partly | The agency's own tests are validated mechanically and rated by three models for rejecting valid solutions, without human review (NTB-0004, `data/kvalitet/`). |
| O.d.2 | Test quality is measured with objective metrics such as coverage. | no | No coverage or complexity metric is computed (not in `harness/`). |
| O.e.1 | Fuzz testing covers edge cases. | not applicable | No fuzz testing (NTB-0008). |
| O.e.2 | Fuzz inputs cover the relevant input variations. | not applicable | No fuzz testing (NTB-0008). |
| O.e.3 | Fuzz inputs are ones the code is sensitive to. | not applicable | No fuzz testing (NTB-0008). |
| O.f.1 | End-to-end tests exercise all relevant parts of the code. | not applicable | The tests are the repositories' own unit and integration tests, not end-to-end tests built for the benchmark (`data/tester/`). |
| O.f.2 | Flaky test results are prevented. | partly | The fail-to-pass set had to be stable over three runs before inclusion, but flakiness during P3 was not measured separately (NTB-0003, `data/p22_resultater.jsonl`). |
| O.g.1 | State matching covers all achievable success states. | not applicable | No state matching (NTB-0008). |
| O.g.2 | State matching checks relevant and irrelevant states. | not applicable | No state matching (NTB-0008). |
| O.g.3 | The ground-truth state is complex enough to prevent trivial changes. | not applicable | No state matching (NTB-0008). |
| O.h.1 | Required answer formats are stated. | not applicable | No answer matching; the agent delivers a code change (`harness/agent/innpakning.txt`). |
| O.h.2 | Success by random guessing is minimised. | not applicable | No answer matching (NTB-0008). |
| O.i.1 | Quality metrics resist exploitation. | not applicable | No quality metric; the outcome is pass or fail of the tests (NTB-0008). |

## Benchmark reporting

| ID | Item (paraphrased) | Answer | Basis |
|---|---|---|---|
| R.1 | The benchmark is fully or partly open source. | yes | Tasks, harness, analysis and run files are in this repository under MIT and CC BY 4.0 (LICENSE). |
| R.2 | An open-source evaluation harness is offered. | yes | `harness/` and `analysis/` (README.md). |
| R.3 | There are measures against data contamination at release. | partly | Tasks were merged after the models' training cutoff, carry a canary string, and the set is retired for newer models; there is no held-out set (NTB-0003, NTB-0009, `data/CANARY.md`). |
| R.4 | There are measures or plans to update the tasks over time. | partly | Refills with new months of merged pull requests are planned as a later version and not carried out (IDEER.md, NTB-0009). |
| R.5 | The link between the capabilities evaluated and what is measured is stated. | yes | The purpose and what v1.0 does not measure are stated (NTB-0001, PREREG.md). |
| R.6 | What is evaluated (model or agent framework) is stated. | yes | The arms are Claude Code 2.1.325 with two named models, with fixed flags and wrapper (PREREG.md, question 4). |
| R.7 | Steps to prevent, find and correct flaws are described. | yes | Sealing, self-test, grading-path check, quality check and recorded deviations (NTB-0006, NTB-0014, NTB-0004, AVVIK.md). |
| R.8 | The possible impact of unavoidable flaws is discussed qualitatively. | yes | RESULTATER.md, section «Limits», and PREREG.md, section «Limits». |
| R.9 | The impact of unavoidable flaws is analysed quantitatively. | partly | The main measure is reported with and without flagged tasks, by quality-check outcome, and with and without the supplementary runs, but the effect of the extended text's knowledge of the solution is not measured (RESULTATER.md tables T7 and T10). |
| R.10 | Statistical uncertainty is reported, such as confidence intervals. | yes | 95 % intervals per task and clustered on repository (`analysis/analyse.py`, RESULTATER.md). |
| R.11 | Guidance on interpreting results with evaluation flaws is given. | yes | RESULTATER.md, section «Limits», items a–g. |
| R.12 | Results of non-AI baselines, such as human experts, are reported. | no | No human baseline; comparison with human time is excluded (NTB-0008). |
| R.13 | Results of trivial agents, such as one that does nothing, are reported. | yes | The empty patch gives not solved for every task in validation and in the grading-path check (`data/p22_resultater.jsonl`, NTB-0014). |
