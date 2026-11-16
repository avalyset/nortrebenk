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
5. The patch is graded in a fresh container from the instance image without network: base, agent patch and test patch. The task is resolved when all f2p and p2p tests pass.
