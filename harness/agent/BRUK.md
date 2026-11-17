# Agent run (NTB-0006, NTB-0007)

Claude Code is run as an agent in a container with no route out. The only way out is a proxy that forwards to the model API.

## Contents

- `agentbilde.py`: build recipe for the agent image.
  - The same pinned base image, setup, installation and warm-up as the instance image in `harness/msb_repos/`.
  - The image has no gold patch, test patch or run scripts.
  - The repo, the git sealing and the dependency cache are owned by the user `agent`. Claude Code refuses `--dangerously-skip-permissions` as root.
  - Claude Code is included as a standalone binary, pinned to a version (`CC_VERSJON`) and checked against the sha256 from the version's manifest.
  - The environment points to the proxy, has a placeholder as key and turns off telemetry, error reporting, updates and other non-essential traffic.
- `mellomtjener.py`: forwards only paths under `/v1/` to api.anthropic.com, with streaming.
  - The key is read from the environment variable `NTB_UPSTREAM_KEY` and set as `x-api-key`. Incoming key headers are removed.
  - Calls with server-side tools for web search or web fetch are rejected with 400, and other paths with 403.
  - The log has time, method, path, status and whether the call was rejected, never content or headers.
- `selvtest.sh`: self-test without model calls. It is run in a fresh container before each agent run and checks five things:
  - that no files are named `fix.patch`, `test.patch`, `run-B.sh` or `run-C.sh`;
  - that the gold patch's three longest added lines are not found under `/home`, `/root` or `/tmp`;
  - that github.com and the package registries cannot be reached;
  - that the environment has no key;
  - that git has one commit, no remotes and one ref.
- `kjor_agent.py`: network and proxy, build, self-test (also with model calls), check of the grading path, agent run and grading.
- `takregel.py`: the cap rules for a run (NTB-0014, changed 2026-11-17), as pure functions used by `kjor_agent.py`.
- `kjor_p3.py`: the P3 runner (NTB-0014): run plan, passes, budget, restart and the dress rehearsal mode `prove`.
- `innpakning.txt`: the fixed wrapper around the task's title and description, the same for all tasks and arms.
- `budsjett.py`: creates `data/roykprove/kjoringer.jsonl` and `budsjett.md` from the run files.

## Running

Requirements: Docker and Python with multi-swe-bench (commit 24f493f) and the Docker SDK for Python. The paths are set with environment variables:

- `NTB_MSB_REPOS`: the repo definitions, `harness/msb_repos`.
- `NTB_OPPGAVER`: folder with `<org>__<repo>__<pr>.json`, with the fields `org`, `repo`, `pr`, `url`, `basis_sha`, `tittel` and `beskrivelse`.
- `NTB_PATCHER`: folder with `<org>__<repo>__<pr>/test.patch` and `fix.patch`.
- `NTB_TESTER`: folder with `<org>__<repo>__<pr>.json`, with the lists `f2p` and `p2p`.
- `NTB_UT`: logs, transcripts, patches and results.

```bash
python harness/agent/kjor_agent.py nett                         # internt nett ntb-agent og mellomtjener
python harness/agent/kjor_agent.py bygg <id>                     # agentbilde
python harness/agent/kjor_agent.py selvtest <id> --modell        # selvtest med de to modellkallene
python harness/agent/kjor_agent.py kontroll <id>                 # gullpatch utenom test gir løst, tom patch ikke
python harness/agent/kjor_agent.py kjor <id> claude-sonnet-5-5 1.50
```

`nett` reads the key from `ANTHROPIC_API_KEY_NORDVAULT` in the process environment. The key is given to the proxy with `docker run -e NTB_UPSTREAM_KEY` without a value, so it never appears on a command line and never exists in the agent container.

A run does this:
1. The self-test is run first. If it fails, the agent is not run.
2. The agent is run with `claude -p`, `--output-format stream-json --verbose`, `--dangerously-skip-permissions`, `--disallowedTools WebSearch WebFetch` and `--max-budget-usd`. The runner has a time limit of 40 minutes.
3. The patch is all changes against the single commit. Files the warm-up created before the agent started are excluded.
4. Changes to files that the test patch touches are discarded.
5. The patch is graded in a fresh container from the instance image without network: base, agent patch and test patch. The tests' outcome is stored in `loest_for_takregel` (all f2p and p2p tests pass).
6. `loest` is `loest_for_takregel` only if no cap was hit; a run that hits the budget cap or the time cap is not resolved.
7. If the time cap stopped the run before Claude Code reported a cost, `total_cost_usd` is set to the run's budget cap and `kostnad_satt_til_tak` is true; otherwise `kostnad_satt_til_tak` is false.

The time cap is `timeout -k 30` around `claude`: after 40 minutes Claude Code gets SIGTERM, and SIGKILL 30 seconds later. If the `docker run` around it times out, the container is removed before the error is passed on. If the self-test fails, `kjor_agent.kjør()` raises `Selvtestfeil`; it raises `SystemExit` only if the API key prefix is found in the transcript.

## P3 runner

```bash
python harness/agent/kjor_p3.py plan                                    # data/p3_plan.jsonl, without Docker
python harness/agent/kjor_p3.py kontroll <id>...                        # everything except the agent runs
python harness/agent/kjor_p3.py kjor --saldo <USD>                      # P3; refuses until PREREG_DOI.txt exists
python harness/agent/kjor_p3.py prove --sett <fil> --instanser <fil> --saldo <USD>
```

`prove` is the dress rehearsal: the same loop as `kjor`, with the PR text only and one pass, for tasks outside the set. It refuses any task whose ID is in `data/sett_v1.jsonl` and does not use the `PREREG_DOI.txt` guard. The task file and the instance file have the same schema as `data/sett_v1.jsonl` and `data/instances.jsonl`.

The runner writes to `NTB_UT`: `p3_kjoringer.jsonl` (one line per attempt, with `pass`, `nummer`, `oppgave`, `tekstvariant`, `arm`, `forsok`, `status` and the run fields), `p3_pass.jsonl` (one line per pass), `p3_logg.jsonl` and `p3_start.json`.

- Budget check: before every attempt, reruns included, the runner checks that amount spent plus the run's cap does not exceed B. If it does, the pass is stopped by the budget and is incomplete.
- Self-test: if the self-test fails immediately before a run, it is tried once more. If it fails again, that run and the task's remaining runs in the pass stand as missing (`selvtest feilet før kjøring`), and the runner goes on to the next task.
- Disk gate: if less than 6 GiB is free on `NTB_DISK` after cleanup, the build is not started and the task's runs in the pass stand as missing (`under 6 GiB ledig`). The same holds in `kontroll` mode.

Restart: if the runner stops for a reason outside these rules, it is started again with the same command and the same `NTB_UT`.
- On the first start, `p3_start.json` is written with B and the time. Later starts use B from there, whatever `--saldo` says.
- Amount spent is the sum of `total_cost_usd` over all lines in `p3_kjoringer.jsonl`.
- Completed passes are read from `p3_pass.jsonl`. If that file has a pass with `fullfort` false (stopped by the budget), the runner refuses to continue.
- In the pass in progress, runs with status `gjennomfort` or `manglende` are skipped; the key is (pass, task, text variant, arm). Discarded attempts keep counting towards the limit of two reruns. A run that was in progress is run again. Tasks with no remaining runs are not built.
