# Instrument anchor for the runner: Altinn/app-frontend-react in Multi-SWE-bench

Read 2026-11-16.

Multi-SWE-bench (commit 24f493f) has three definitions for Altinn/app-frontend-react under `multi_swe_bench/harness/repos/typescript/Altinn/` (see `data/dedup.md`). The anchor was to compare our f2p and p2p lists with the dataset's lists for the three instances with the highest PR numbers.

**Finding: the dataset has no instances for Altinn/app-frontend-react.** The comparison could therefore not be made, and part D stopped after the first step.

| Dataset | How it was read | Instances for Altinn/app-frontend-react |
|---|---|---|
| ByteDance-Seed/Multi-SWE-bench | file list (59 entries); no file for Altinn | 0 |
| ByteDance-Seed/Multi-SWE-RL | file list (154 entries); no file for Altinn | 0 |
| ByteDance-Seed/Multi-SWE-bench_mini | whole file searched for «altinn» | 0 |
| ByteDance-Seed/Multi-SWE-bench-flash | whole file searched for «altinn» | 0 |

| Comparison (D3) | Theirs | Ours | Common | Only theirs | Only ours | Reproduced |
|---|---|---|---|---|---|---|
| not possible | – | – | – | – | – | – |

The runner is thus not anchored against published test lists in v1.0.
