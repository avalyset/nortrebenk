# Overlap with existing sets

## SWE-rebench V2

Checked 2026-11-16. Source: the dataset nebius/SWE-rebench-V2 on Hugging Face, the file `data/train-00000-of-00001.parquet` (the only parquet file). Only the column `repo` was read, with duckdb and column selection.

**Answer: none of the repos in nortrebenk are in SWE-rebench V2.** No repo in the dataset starts with `navikt/` or `Altinn/` (case-insensitive).

Check (passed):
- rows read: 32079
- unique repos: 3617
- `elastic/synthetics` is present: yes (44 rows)

## Multi-SWE-bench

Definitions under `multi_swe_bench/harness/repos/` in multi-swe-bench, commit 24f493f, for the organizations navikt and Altinn:

- navikt: none
- Altinn (typescript): `app_frontend_react_1534_to_724`, `app_frontend_react_3503_to_2448`, `app_frontend_react_713_to_683` (all three concern the repo Altinn/app-frontend-react)

Altinn/app-frontend-react is not among the repos in nortrebenk.
