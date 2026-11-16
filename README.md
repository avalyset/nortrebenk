# nortrebenk

nortrebenk measures how well and how fast coding agents solve tasks taken from public code in Norwegian public agencies, and what each solved task costs. The tasks are merged pull requests from the agencies' public GitHub repositories, and the ground truth is the agency's own tests: a task counts as solved when the tests that failed before the change pass, and the tests that passed still pass.

**Status: in development, not published.** The preregistration for the pilot measurement is a draft ([PREREG.md](PREREG.md)); no agent has been run on a task in the set.

## Contents

- Task set: [data/sett_v1.jsonl](data/sett_v1.jsonl), 21 tasks from 5 repositories (source: `data/sett_v1.jsonl`); patches in [data/instances.jsonl](data/instances.jsonl); canary in [data/CANARY.md](data/CANARY.md).
- Two text variants per task: the PR text and an extended text with requirements and interface ([data/utvidet_tekst.jsonl](data/utvidet_tekst.jsonl), NTB-0013).
- Quality check of the tasks: [data/kvalitet/](data/kvalitet/) (in Norwegian; the files under `data/kvalitet/` and `data/roykprove/` are kept unchanged).
- Harness: [harness/BRUK.md](harness/BRUK.md) (validation images), [harness/agent/BRUK.md](harness/agent/BRUK.md) (agent runs), `harness/agent/kjor_p3.py` (run plan for P3, 252 runs in `data/p3_plan.jsonl`), `harness/sett/lag_sett.py`, `harness/tekst/`, `harness/kvalitet/`.
- Analysis: `analysis/analyse.py`. Tests: `python -m unittest discover -s tests`.
- Plan: [PLAN.md](PLAN.md). Decisions: [docs/decisions/](docs/decisions/). Deviations: [AVVIK.md](AVVIK.md). Ideas: [IDEER.md](IDEER.md).

## Limits

- v1.0 is a task set, a repeatable method and a preregistered pilot measurement. It is not a ranking of agents, not a picture of the agencies' code, not a measure of licence value, not a measurement of a human working with an agent and not a measurement of GitHub Copilot (NTB-0001).
- v1.0 measures one vendor, Anthropic (NTB-0012).
- The agent setup is not anchored to published solve rates (NTB-0007).
- The quality-check anchor consists of English-language Python tasks the models may have seen in training, including the outcome of the annotation; the set is Kotlin and TypeScript with Norwegian and English text (NTB-0004). The Google rater was a free-tier model (AVVIK.md no. 4).
- The extended text was added after the outcome of the quality check of the PR text (P2.3) and the smoke test were known, and before any agent run on a set task. The additions were written by a model from the same vendor as the agents, without human review; that a task passes the quality check may rest on the rater from the same vendor; and the additions state names and strings from the solution (NTB-0013, AVVIK.md no. 7).
- Measurement platform is linux/arm64, local. A cross-check on amd64 through unmodified Multi-SWE-bench harness is run before v1.0 only if included credit covers it (NTB-0011). The runner anchor against Multi-SWE-bench fell away because the dataset has no instances for the repository that was to be used (AVVIK.md no. 5).
- The tasks come from five repositories; tasks from the same repository are not independent, and clustered standard errors with five clusters are uncertain (NTB-0008).

## Sammendrag (norsk)

nortrebenk måler hvor godt og raskt kodeagenter løser oppgaver fra offentlig kode i norske etater, og hva hver løste oppgave koster. Fasiten er etatens egne tester. Oppgavesettet har 21 oppgaver fra 5 repoer (kilde: `data/sett_v1.jsonl`), hver med to tekstvarianter: PR-teksten og en utvidet tekst med krav og grensesnitt. Pilotmålingen er forhåndsregistrert som utkast og er ikke kjørt. Dokumentene er på engelsk; feltnavnene i datafilene er norske og forklart i ordlista under.

## Glossary of Norwegian field names

| Field | Meaning |
|---|---|
| `agentmarkor` | agent marker: whether the PR text or commit messages mark the change as made with a coding agent (ja/nei = yes/no) |
| `arm` | arm: the model the agent runs with |
| `avgjorende_kriterier` | deciding criteria: criteria where one more vote could change the outcome |
| `bygg` | build: extra build fields for the task (dependency caches from the gold-patch state) |
| `budsjett_usd / budsjettak_slo_inn` | budget per run in USD / whether the budget cap was hit |
| `cacher_fra_gulltilstand` | caches taken from the gold-patch state |
| `ekstra_miljo` | extra environment setting in the image |
| `forkastede_testfilendringer` | number of discarded agent changes to files the test patch touches |
| `forsegling, forsegling_kontrollert` | sealing / sealing checked (one commit, no remotes, one ref) |
| `forsok` | attempt number |
| `gullpatch` | gold patch: the non-test part of the merged PR |
| `ikke_pass` | tests among f2p and p2p that did not pass |
| `i_settet_etter_p22` | in the set after P2.2 (ja/nei) |
| `kalt` | called: whether the rater was called |
| `kjoring` | run identifier |
| `kodesprak` | code language |
| `lisens` | licence |
| `loest, loest_B, loest_C_antall` | solved; solved in run B (test patch only); number of solved runs C (test patch and gold patch) |
| `mellomtjener_kall / mellomtjener_avvist` | requests through the proxy / requests the proxy rejected |
| `merged` | time the PR was merged |
| `modell, modell_svar` | model ID requested / model ID in the response |
| `nummer` | position in the run order within a pass |
| `oppgave, oppgavetekst` | task / task text |
| `ordrett_andel` | verbatim share: share of the gold patch's added lines (at least 8 characters) that appear verbatim in the text |
| `parametre` | request parameters |
| `pass` | pass number in P3 |
| `pr_tekst, utvidet_tekst` | PR text (title and description) / extended text (PR text with requirements and interface) |
| `regel` | decision rule of the rater ensemble |
| `stemmer_for_utelukkelse` | votes for exclusion |
| `tekstsprak` | text language of the PR text (norsk/engelsk/blandet = Norwegian/English/mixed) |
| `tekstvariant` | text variant (pr_tekst or utvidet) |
| `testpatch, testpatch_kompilerer_mot_base` | test patch / whether the test patch compiles against the base (ja/nei/delvis = yes/no/partly) |
| `tidstak_slo_inn` | whether the time cap was hit |
| `trenger_nett_i_test` | whether the tests needed network |
| `utfall, utfall_p23, utfall_p23b` | outcome; outcome of the quality check in P2.3 / P2.3b (består/utelukket = passes/excluded) |
| `utelukket_paa` | criteria the task was excluded on |
| `veggtid_s` | wall time in seconds |
| `vurderer` | rater |

## Licence

Code under MIT, documentation and data under CC BY 4.0 (see [LICENSE](LICENSE)).
