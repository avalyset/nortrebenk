# Overlapp med eksisterende sett

## SWE-rebench V2

Sjekket 2026-11-16. Kilde: datasettet nebius/SWE-rebench-V2 på Hugging Face, fila `data/train-00000-of-00001.parquet` (eneste parquet-fil). Bare kolonnen `repo` ble lest, med duckdb og kolonneutvalg.

**Svar: ingen av repoene i nortrebenk finnes i SWE-rebench V2.** Ingen repo i datasettet starter med `navikt/` eller `Altinn/` (uten skille mellom store og små bokstaver).

Kontroll (bestått):
- rader lest: 32079
- unike repoer: 3617
- `elastic/synthetics` finnes: ja (44 rader)

## Multi-SWE-bench

Definisjoner under `multi_swe_bench/harness/repos/` i multi-swe-bench, commit 24f493f, for organisasjonene navikt og Altinn:

- navikt: ingen
- Altinn (typescript): `app_frontend_react_1534_to_724`, `app_frontend_react_3503_to_2448`, `app_frontend_react_713_to_683` (alle tre gjelder repoet Altinn/app-frontend-react)

Altinn/app-frontend-react er ikke blant repoene i nortrebenk.
