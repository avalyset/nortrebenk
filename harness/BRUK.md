# Using the harness (P2.2)

The harness builds one sealed Docker image per task and runs the task's tests in new containers. It uses the classes in Multi-SWE-bench (commit 24f493f): `PullRequest`, `Config`, `Image` and `Instance`. The run goes through an own, thin runner, because Multi-SWE-bench's test run (swe-rex and `nix_swe`) exists only for linux/amd64. P2.2 was run on linux/arm64.

## Contents

- `msb_repos/_felles.py`: shared code. Builds the sealed image, creates the run scripts and reads JUnit XML and TRX.
- `msb_repos/<org>/<repo>.py`: one definition per repo. The base image is pinned by digest. The definition has setup, installation, warm-up and test command.
- `scripts/p22_kjor.py`: runs all tasks in one repo.

## Sealed image

1. The repo is cloned in a separate build stage and checked out at `base_sha`. The `.git` folder is deleted.
2. The working tree is copied into the final image, which gets a new git repo with one commit. It has no remotes and no other refs.
3. The dependencies are installed after the sealing. The warm-up runs the tests once, so that the build tool's cache is filled.
4. The image itself checks that `git log --all` gives one commit, that `git remote -v` is empty and that there is only one ref. Only then is `/home/forsegling.txt` written.

The runs do not use `git fetch` or `git clean -x`.

## Runs

- **B**: the test patch is applied on base. Run once, with network.
- **C**: the test patch and the gold patch are applied on base. Run three times, each time in a new container. The first C is run with `--network none`. If it fails because of network, `trenger_nett_i_test: true` is set, and all three C runs are run with network.

A task is resolved when all tests in the P1 lists `f2p` and `p2p` have PASS.

The task is included in the set (`i_settet_etter_p22: ja`) when four conditions are met:
- B is not resolved.
- C is resolved in all three runs.
- The run was completed.
- The sealing is checked.

## Running

Requirements:
- Docker
- Python 3.12 with multi-swe-bench (commit 24f493f, `uv pip install -e .`) and `docker` (Python SDK)

The runner reads three paths from environment variables:

- `NTB_P1`: folder with `results.jsonl` (P1 status per task; tasks with `status: validert` are run), `c2_patcher.jsonl` (one line per task with `url`, `repo`, `pr`, `basis_sha` and `deps_reinstall`) and `tester/<org>__<repo>__<pr>.json` (lists `f2p` and `p2p`). `data/p1_resultater.jsonl` and `data/tester/` in this repo have the same content.
- `NTB_PATCHER`: folder with `<org>__<repo>__<pr>/test.patch` and `fix.patch`. The patches for the tasks in the set are in `data/instances.jsonl` (the fields `testpatch` and `gullpatch`).
- `NTB_UT`: folder for logs, build folders and results (default `ntb-ut`).

```bash
NTB_P1=... NTB_PATCHER=... NTB_UT=ntb-ut python harness/scripts/p22_kjor.py navikt/mock-oauth2-server 2
```

The last argument is the number of tasks run in parallel (default 2). Each task has a time limit of 40 minutes. The result for each task is written to `$NTB_UT/res/<org>__<repo>__<pr>.json`, and the logs to `$NTB_UT/logs/<org>__<repo>__<pr>/`.

On import errors on macOS: multi-swe-bench 24f493f has both `repos/python/Qiskit` and `repos/python/qiskit`, which collide on file systems that do not distinguish between upper and lower case. The runner therefore replaces the combined repo import with an empty module.
