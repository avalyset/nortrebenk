# Instrumentanker for kjøreren: Altinn/app-frontend-react i Multi-SWE-bench

Lest 2026-11-16.

Multi-SWE-bench (commit 24f493f) har tre definisjoner for Altinn/app-frontend-react under `multi_swe_bench/harness/repos/typescript/Altinn/` (se `data/dedup.md`). Ankeret skulle sammenligne våre f2p- og p2p-lister med datasettets lister for de tre instansene med høyest PR-nummer.

**Funn: datasettet har ingen instanser for Altinn/app-frontend-react.** Sammenligningen kunne derfor ikke gjøres, og del D stoppet etter første steg.

| Datasett | Hvordan det er lest | Instanser for Altinn/app-frontend-react |
|---|---|---|
| ByteDance-Seed/Multi-SWE-bench | fillista (59 oppføringer); ingen fil for Altinn | 0 |
| ByteDance-Seed/Multi-SWE-RL | fillista (154 oppføringer); ingen fil for Altinn | 0 |
| ByteDance-Seed/Multi-SWE-bench_mini | hele fila søkt etter «altinn» | 0 |
| ByteDance-Seed/Multi-SWE-bench-flash | hele fila søkt etter «altinn» | 0 |

| Sammenligning (D3) | Hos dem | Hos oss | Felles | Bare hos dem | Bare hos oss | Reprodusert |
|---|---|---|---|---|---|---|
| ikke mulig | – | – | – | – | – | – |

Kjøreren er dermed ikke ankret mot publiserte testlister i v1.0.
