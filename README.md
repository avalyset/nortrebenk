# nortrebenk

nortrebenk measures how well and how fast coding agents solve tasks taken from public code in Norwegian public agencies, and what each solved task costs. The tasks are merged pull requests from the agencies' public GitHub repositories. The ground truth is the agency's own tests: a task counts as solved when the tests that failed before the change pass, and the tests that passed still pass.

**Status: v1.0. Preregistered at git tag `prereg-v1` ([PREREG.md](PREREG.md), DOI [10.5281/zenodo.24304903](https://doi.org/10.5281/zenodo.24304903)); the pilot was run on 17–18 November 2026. Results are in [RESULTATER.md](RESULTATER.md), and deviations no. 9–12 are in [AVVIK.md](AVVIK.md).**

## Contents

- Task set: [data/sett_v1.jsonl](data/sett_v1.jsonl), 21 tasks from 5 repositories (source: `data/sett_v1.jsonl`); patches in [data/instances.jsonl](data/instances.jsonl); canary in [data/CANARY.md](data/CANARY.md).
- Two text variants per task: the PR text, and an extended text with requirements and interface ([data/utvidet_tekst.jsonl](data/utvidet_tekst.jsonl), NTB-0013).
- Quality check of the tasks: [data/kvalitet/](data/kvalitet/), including the independent check ([data/kvalitet/uavhengig.md](data/kvalitet/uavhengig.md)). Smoke test, dress rehearsal of the runner and budget: [data/roykprove/](data/roykprove/).
- Harness: [harness/BRUK.md](harness/BRUK.md) (validation images), [harness/agent/BRUK.md](harness/agent/BRUK.md) (agent runs), `harness/agent/kjor_p3.py` (run plan for P3, 252 runs in `data/p3_plan.jsonl`), `harness/sett/lag_sett.py`, `harness/tekst/`, `harness/kvalitet/`.
- Pilot run files: [data/p3/](data/p3/): `p3_kjoringer.jsonl` (the registered runs without the field `resultat_tekst`), `p3_pass.jsonl` and `p3_tillegg.jsonl` (the four supplementary runs, AVVIK.md no. 9).
- Results: [RESULTATER.md](RESULTATER.md); [results/](results/) holds the output of the locked analysis (`p3_registrert.json`, `p3_med_tillegg.json`), the tables (`tabeller.md`) and the exchange rate (`valutakurs.json`).
- Analysis: `analysis/analyse.py` (locked at `prereg-v1`) and `analysis/lag_resultater.py` (formats the tables, adds no statistic; AVVIK.md no. 11). Tests: `python -m unittest discover -s tests`.
- Datasheet: [docs/DATASHEET.md](docs/DATASHEET.md). Agentic Benchmark Checklist: [docs/ABC_CHECKLIST.md](docs/ABC_CHECKLIST.md).
- Plan: [PLAN.md](PLAN.md). Decisions: [docs/decisions/](docs/decisions/). Deviations: [AVVIK.md](AVVIK.md). Ideas: [IDEER.md](IDEER.md).

## Limits

- v1.0 is a task set, a repeatable method and a preregistered pilot measurement. It is not a ranking of agents, not a picture of the agencies' code, not a measure of licence value, not a measurement of a human working with an agent and not a measurement of GitHub Copilot (NTB-0001).
- v1.0 measures one vendor, Anthropic (NTB-0012).
- The agent setup is not anchored to published solve rates (NTB-0007).
- The quality-check anchor consists of English-language Python tasks the models may have seen in training, including the outcome of the annotation. The set is Kotlin, TypeScript and C# with Norwegian and English text (NTB-0004). The Google rater was a free-tier model (AVVIK.md no. 4).
- The extended text was added after the outcome of the quality check of the PR text (P2.3) and the smoke test were known, and before any agent run on a set task. The additions were written by a model from the same vendor as the agents, without human review; a task's pass in the quality check may rest on the rater from the same vendor; and the additions state names and strings from the solution (NTB-0013, AVVIK.md no. 7).
- The measurement platform is linux/arm64, local. The cross-check on amd64 through the unmodified Multi-SWE-bench harness (NTB-0011) was not run (AVVIK.md no. 12). The runner anchor against Multi-SWE-bench fell away because the dataset has no instances for the repository that was to be used (AVVIK.md no. 5).
- The tasks come from five repositories. Tasks from the same repository are not independent, and clustered standard errors with five clusters are uncertain (NTB-0008).
- Sample: 21 tasks from 5 repositories in two GitHub organisations, navikt and Altinn, merged between 2026-11-02T12:58:35Z and 2026-11-14T23:10:08Z (source: `data/sett_v1.jsonl`).
- Validation was done with an own runner on linux/arm64, not through unmodified Multi-SWE-bench (AVVIK.md no. 1).

## Validity (NTB-0009)

The set is valid for models with a training cutoff before 2026-11-02T12:58:35Z, the earliest merge date in the set (source: `data/sett_v1.jsonl`). For newer models it is retired.

## Related work

- Stray et al. (arXiv:2509.20353) report a mixed-methods case study of developer productivity with and without GitHub Copilot in NAV IT, a large public-sector agile organisation.
- The Government Digital Service's «AI coding assistant trial» (gov.uk, 12 September 2025) aimed to understand how such tools could help public-sector engineering and development teams.
- RuBench (arXiv:2607.06411) is a repository-level agentic coding benchmark whose task specifications are written natively in Russian, not translated.
- Multi-SWE-bench (arXiv:2504.02605) is a multilingual issue-resolving benchmark covering Java, TypeScript, JavaScript, Go, Rust, C and C++. Its harness has definitions for Altinn/app-frontend-react, and its published datasets have no instances for that repository ([data/anker/msb_altinn.md](data/anker/msb_altinn.md)).

## Sammendrag (norsk)

nortrebenk måler hvor godt og hvor raskt kodeagenter løser oppgaver fra offentlig kode i norske etater, og hva hver løste oppgave koster. Fasiten er etatens egne tester. Settet har 21 oppgaver fra 5 repoer hos Nav og Digdir/Altinn (kilde: `data/sett_v1.jsonl`). Hver oppgave har to tekstvarianter: PR-teksten slik den sto, og en utvidet tekst med krav og grensesnitt.

Pilotmålingen er forhåndsregistrert (DOI 10.5281/zenodo.24304903) og ble kjørt 17.–18. november 2026 med Claude Code og to modeller, i tre fullførte pass. Resultatene står i RESULTATER.md, og avvik nr. 9–12 i AVVIK.md.

- **Utvidet tekst (hovedmålet):** claude-sonnet-5-5 løste alle 21 oppgavene i alle kjøringene (løst andel 100 %). claude-opus-5-5 løste 20 av 21 oppgaver i alle kjøringene og én ikke i noen (95,2 %).
- **PR-tekst alene:** løst andel 21,4 % for claude-sonnet-5-5 og 26,2 % for claude-opus-5-5.
- **Forskjellen mellom tekstvariantene:** 78,6 prosentpoeng for claude-sonnet-5-5 og 69,0 for claude-opus-5-5, parvis per oppgave i pass 1 og 2.
- **Kvalitetssjekken av PR-teksten:** de 4 oppgavene som besto den, ble løst i alle kjøringene med PR-teksten alene, av begge modellene. For de 17 som ikke besto, var løst andel 2,9 % for claude-sonnet-5-5 og 8,8 % for claude-opus-5-5.
- **Kostnad per løste oppgave:** 1,10 kr for claude-sonnet-5-5 og 3,76 kr for claude-opus-5-5 på utvidet tekst, og 5,91 kr og 15,80 kr på PR-tekst alene (9,6237 kr per USD, Norges Bank 17.11.2026).

Hovedmålet ligger i taket for begge modellene, så piloten skiller dem ikke. Den utvidede teksten er skrevet med kjennskap til løsningen og oppgir navn og strenger fra den, så løst andel er trolig høyere enn for en spesifikasjon skrevet uten den kjennskapen. PR-teksten alene besto ikke kvalitetssjekken for 17 av 21 oppgaver, så tallene for PR-tekst beskriver for det meste underspesifiserte oppgaver. Tallene gjelder disse 21 oppgavene. Dokumentene er på engelsk; feltnavnene i datafilene er norske, og de mest brukte forklares i ordlista under.

## Glossary of Norwegian field names

| Field | Meaning |
|---|---|
| `agentmarkor` | agent marker: whether the PR text or commit messages mark the change as made with a coding agent (ja/nei = yes/no) |
| `arm` | arm: the model the agent runs with |
| `avgjorende_kriterier` | deciding criteria: criteria where one more vote could change the outcome |
| `bygg` | build: extra build fields for the task (dependency caches from the gold-patch state) |
| `budsjett_usd / budsjettak_slo_inn` | budget per run in USD / whether the budget cap was hit |
| `cacher_fra_gulltilstand` | caches taken from the gold-patch state |
| `claude_code` | Claude Code version used in the run |
| `ekstra_miljo` | extra environment setting in the image |
| `forkastede_testfilendringer` | number of discarded agent changes to files the test patch touches |
| `forsegling, forsegling_kontrollert` | sealing / sealing checked (one commit, no remotes, one ref) |
| `forsok` | attempt number |
| `fullfort` | completed: whether the pass is completed (all planned runs done or recorded as missing) |
| `grunn` | reason: the reason code for a missing run |
| `gullpatch` | gold patch: the non-test part of the merged PR |
| `ikke_pass` | tests among f2p and p2p that did not pass |
| `i_settet_etter_p22` | in the set after P2.2 (ja/nei) |
| `kalt` | called: whether the rater was called |
| `kjoreklasse` | run class of a candidate (A, B or not set); class B is tests that need Testcontainers, Docker, Kafka, Postgres or similar (IDEER.md) |
| `kjoring` | run identifier |
| `kodesprak` | main code language of the repository |
| `kost, kost_utvidet` | cost of the pass / cost of the pass's runs with extended text (USD) |
| `kostnad_satt_til_tak` | whether the run's budget cap was recorded as its cost because no cost was reported |
| `lisens` | licence |
| `loest, loest_B, loest_C_antall` | solved; solved in run B (test patch only); number of solved runs C (test patch and gold patch) |
| `loest_for_takregel` | outcome of the tests before the rule that a run hitting a cap counts as not solved |
| `mellomtjener_kall / mellomtjener_avvist` | requests through the proxy / requests the proxy rejected |
| `merged` | time the PR was merged |
| `modell, modell_svar` | model ID requested / model ID in the response |
| `nummer` | position in the run order within a pass |
| `oppgave, oppgavetekst` | task / task text |
| `ordrett_andel` | verbatim share: share of the gold patch's added lines (at least 8 characters) that appear verbatim in the text |
| `parametre` | request parameters |
| `pass` | pass number in P3 |
| `patch_linjer, patch_feilet` | lines in the agent's patch after test files are removed / whether applying the patch failed in grading |
| `pr_tekst, utvidet_tekst` | PR text (title and description) / extended text (PR text with requirements and interface) |
| `regel` | decision rule of the rater ensemble |
| `sk_ant_i_transkript` | whether the prefix of an Anthropic API key was found in the run's transcript |
| `status, taktest` | run status (gjennomfort/forkastet/manglende = completed/discarded/missing) / which cap a rehearsal run provoked (budsjett/tid = budget/time) |
| `stemmer_for_utelukkelse` | votes for exclusion |
| `tekstsprak` | text language of the PR text (norsk/engelsk/blandet = Norwegian/English/mixed) |
| `tekstvariant` | text variant (pr_tekst or utvidet) |
| `testpatch, testpatch_kompilerer_mot_base` | test patch / whether the test patch compiles against the base (ja/nei/delvis = yes/no/partly) |
| `tid_utc` | time the row was written (UTC) |
| `tidstak_slo_inn` | whether the time cap was hit |
| `tillegg` | supplement: the row is one of the four supplementary runs (AVVIK.md no. 9) |
| `trenger_nett_i_test` | whether the tests needed network |
| `type, varianter` | pass type (fullt/utvidet = full/extended text only) / text variants in the pass |
| `utfall, utfall_p23, utfall_p23b` | outcome; outcome of the quality check in P2.3 / P2.3b (består/utelukket = passes/excluded) |
| `utelukket_paa` | criteria the task was excluded on |
| `utgangskode` | exit code of the agent command in the container |
| `veggtid_s` | wall time in seconds |
| `vurderer` | rater |

## Licence

Code under MIT. Documents and the study's own data and results under CC BY 4.0. Code, tests and pull-request text from the source repositories keep the licence of each source repository (data/LISENSER/). See [LICENSE](LICENSE).

## Funding and disclosure

No grant. The work was done by the author at EcoDeco AS. The Anthropic API use in the study (the agent runs, the extended texts and one of the three raters) was paid with the monthly API credit included in the author's own Claude Max subscription, shown in the Anthropic Console as «API credit (Max)». No credit was granted for the study, and Anthropic had no role in it.

AI disclosure: implemented with Claude Code.
