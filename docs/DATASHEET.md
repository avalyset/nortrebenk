# Datasheet: nortrebenk v1.0

Written after the questions in Gebru et al., «Datasheets for Datasets», arXiv:1803.09010v8 (https://arxiv.org/abs/1803.09010, retrieved 2026-11-18T06:17:32Z), sections 3.1–3.7. The questions are paraphrased. Answers use only what is in this repository; where the repository has no answer, the answer is «not recorded» or «not applicable».

The dataset is the task set (`data/sett_v1.jsonl`, `data/instances.jsonl`, `data/utvidet_tekst.jsonl`, `data/tester/`) together with the study's own data (quality ratings, validation results and the pilot run files in `data/p3/`).

## Motivation

**Purpose of the dataset; specific task; gap.** To measure how well and how fast coding agents solve tasks taken from public code in Norwegian public agencies, and what each solved task costs, with the agency's own tests as the ground truth (NTB-0001, PLAN.md). Related work named in NTB-0001: a mixed-methods case study of developer productivity with and without GitHub Copilot in NAV IT (arXiv:2509.20353); the Government Digital Service's «AI coding assistant trial» for public-sector engineering teams (gov.uk, 12 September 2025); RuBench, a repository-level agentic coding benchmark with task specifications written natively in Russian (arXiv:2607.06411); and Multi-SWE-bench, a multilingual issue-resolving benchmark (arXiv:2504.02605). Multi-SWE-bench has harness definitions for Altinn/app-frontend-react, and its published datasets have no instances for that repository (`data/anker/msb_altinn.md`).

**Who created it, on behalf of which entity.** Eirik Botten Nicolaysen, EcoDeco AS (CITATION.cff).

**Who funded it.** No grant. The work was done by the author at EcoDeco AS. The Anthropic API use (the agent runs, the extended texts and one of the three raters) was paid with the monthly API credit included in the author's own Claude Max subscription, shown in the Anthropic Console as «API credit (Max)»; no credit was granted for the study, and Anthropic had no role in it. The OpenAI rater was paid from EcoDeco AS's prepaid OpenAI API credit, and the Google rater ran on the free tier (AVVIK.md no. 4). The study had no other expenses (NTB-0012).

**Other comments.** v1.0 is a task set, a repeatable method and a preregistered pilot measurement; it is not a ranking of agents and not a picture of the agencies' code (NTB-0001).

## Composition

**What the instances represent.** Each instance is a merged pull request from a public GitHub repository of a Norwegian public agency, turned into a task: the repository at the base commit, a task text, a test patch, a gold patch, and the fail-to-pass and pass-to-pass test lists (`data/instances.jsonl`, `data/sett_v1.jsonl`, `data/tester/`). The study's own data are quality ratings (`data/kvalitet/`), validation results (`data/p1_resultater.jsonl`, `data/p22_resultater.jsonl`, `data/p24_nett.jsonl`) and agent runs (`data/roykprove/`, `data/p3/`).

**How many instances.** 21 tasks from 5 repositories: navikt/mock-oauth2-server 5, Altinn/altinn-access-management-frontend 5, navikt/pensjonssimulator 4, navikt/kafka-manager 4, Altinn/altinn-support-dashboard 3 (source: `data/sett_v1.jsonl`; PREREG.md). The pilot run file has 210 rows and the supplement 4 rows (`data/p3/`).

**All possible instances or a sample.** A sample. The larger set is the candidate list `data/kandidater_v1.jsonl` (194 merged pull requests from the GitHub organisations navikt and Altinn). It is not representative of the agencies' code: inclusion requires that the task runs in a container, builds without a token, has an MIT or Apache-2.0 licence, was merged after the training cutoff of the measured models, is not in Multi-SWE-bench or SWE-rebench V2, and passes the quality check (NTB-0003). Coverage is two agencies, five repositories and two main repository languages (NTB-0001).

**What each instance consists of.** Raw data: repository URL and base commit, the pull-request title and description (`pr_tekst`), an extended text with requirements and interface (`utvidet_tekst`), the test patch, the gold patch, the fail-to-pass and pass-to-pass test names, licence, merge time, code language, text language and agent marker (fields listed in the README glossary).

**Label or target.** The target is the agency's own tests: a task is solved when all fail-to-pass and pass-to-pass tests pass (NTB-0008).

**Missing information.** @-usernames and e-mail addresses were removed from the task texts (NTB-0010); that is intentional removal. Four planned pilot runs are missing in `data/p3/p3_kjoringer.jsonl` (reason code in the rows; RESULTATER.md, AVVIK.md no. 9).

**Relationships between instances.** Tasks from the same repository share code and are not independent; the analysis clusters on repository (NTB-0008). Each task links to its source pull request by URL.

**Recommended splits.** None. All 21 tasks are an evaluation set.

**Errors, noise, redundancies.** Overlap with Multi-SWE-bench and SWE-rebench V2 was checked: none of the repositories are in SWE-rebench V2, and Multi-SWE-bench has no definitions for navikt and only Altinn/app-frontend-react for Altinn, which is not in the set (`data/dedup.md`). The tests may reject valid solutions and the PR text may be underspecified: the PR text alone passed the quality check for 4 of 21 tasks (`utfall_p23` in `data/sett_v1.jsonl`; NTB-0013). The fail-to-pass sets were stable over three runs (`data/p22_resultater.jsonl`).

**Self-contained or relying on external resources.** It relies on the source repositories on GitHub and on the container base images named in the field `base_image`. There is no guarantee that they remain available. The task set records base commits, patches and checksums (`data/SHA256SUMS`). Each source repository has its own licence (MIT for all five; `data/LISENSER/`).

**Confidential data.** Not recorded as present. The source material is public code and public pull-request text.

**Offensive content.** Not recorded.

**Subpopulations.** Not applicable; the instances are code changes, not people.

**Can individuals be identified.** The tasks have no author field, and @-usernames and e-mail addresses are removed from the task text, but the PR URL is kept as the source reference and leads to the public pull request and its author (NTB-0010).

**Sensitive data.** Not recorded.

**Other comments.** Every instance has a canary string (`data/CANARY.md`).

## Collection process

**How the data was acquired.** Directly observable: merged pull requests, their text and their diffs from public GitHub repositories. Derived data: the test lists come from running the tests at base, with the test patch, and with the test patch and gold patch (P1, P2.2; `data/p1_resultater.jsonl`, `data/p22_resultater.jsonl`); the extended text was written by a model (NTB-0013); quality ratings were given by three models (NTB-0004).

**Mechanisms and their validation.** Software: the harness in `harness/` (Multi-SWE-bench classes at commit 24f493f with an own thin runner, NTB-0002). Validation: run validation in P1, stability over three runs and an empty-patch check in P2.2, a grading-path check per task before the agent runs (NTB-0014), and an ensemble of model raters measured against human SWE-bench Verified annotations (agreement in `data/kvalitet/samsvar.md`).

**Sampling strategy.** Deterministic rules applied to the candidate list (NTB-0003). The 30 candidates run in P1 (`data/p1_resultater.jsonl`) are the rows in `data/kandidater_v1.jsonl` with run class A (`kjoreklasse`) and licence MIT (`lisens`); the two sets are equal. How the 194 candidates were collected is not recorded in this repository.

**Who was involved and how they were compensated.** The author; language models as raters and as writers of the extended text. Compensation: not applicable.

**Timeframe.** The pull requests were merged between 2026-11-02T12:58:35Z and 2026-11-14T23:10:08Z (`data/sett_v1.jsonl`). The set was built on 16–17 November 2026 and the pilot was run on 17–18 November 2026 (`data/p3/p3_kjoringer.jsonl`, field `tid_utc`).

**Ethical review.** Not recorded.

**Collected from individuals directly or via third parties.** Via a third party: public GitHub repositories.

**Were individuals notified.** Not recorded.

**Did individuals consent.** Not recorded.

**Mechanism to revoke consent.** Not recorded.

**Data protection impact analysis.** Not recorded. NTB-0010 records the decision on personal data.

**Other comments.** None.

## Preprocessing, cleaning, labelling

**Was preprocessing done.** Yes: the gold patch and test patch were separated from the merged pull request; @-usernames and e-mail addresses were removed from the task text (NTB-0010); tasks were excluded by the inclusion rules (NTB-0003); the extended text was added (NTB-0013). The published pilot run files omit the field `resultat_tekst` (AVVIK.md no. 11).

**Raw data saved.** The source pull requests remain on GitHub (field `url`). The registered pilot run files with `resultat_tekst` are kept by the author and are not published; their sha256 is stated in RESULTATER.md.

**Software available.** Yes: `harness/sett/lag_sett.py`, `harness/tekst/`, `harness/kvalitet/`, `harness/agent/`, `analysis/`.

**Other comments.** None.

## Uses

**Already used for.** The preregistered pilot measurement P3 (PREREG.md, RESULTATER.md).

**Repository linking to papers or systems that use it.** Not recorded.

**Other tasks it could be used for.** Not recorded beyond the ideas in IDEER.md (refill with new months of merged pull requests, other agents and vendors as arms, measurement on an agency's own repositories).

**Composition or collection that might affect future uses.** The set is valid only for models with a training cutoff before the earliest merge date in the set, 2026-11-02T12:58:35Z (NTB-0009). The extended text states names and strings from the solution (NTB-0013). The tasks come from five repositories and two agencies.

**Tasks it should not be used for.** Ranking agents, describing the agencies' code, measuring licence value, measuring a human working with an agent, or measuring GitHub Copilot (NTB-0001). Training models (`data/CANARY.md`).

**Other comments.** None.

## Distribution

**Distributed to third parties.** Yes, publicly (NTB-0009).

**How.** As this repository and a Zenodo deposit. The preregistration has DOI 10.5281/zenodo.24304903 (`PREREG_DOI.txt`). v1.0 has no DOI yet.

**When.** Not recorded.

**Licence.** Code under MIT; documents and the study's own data and results under CC BY 4.0 (LICENSE).

**Third-party restrictions.** Code, tests and pull-request text from the source repositories keep the licence of each source repository: MIT for all five (`data/LISENSER/`).

**Export controls or regulatory restrictions.** Not recorded.

**Other comments.** None.

## Maintenance

**Who maintains it.** The author (CITATION.cff).

**Contact.** The author's ORCID record, https://orcid.org/0009-0001-9188-6788 (CITATION.cff).

**Erratum.** Deviations are recorded in AVVIK.md.

**Updates.** v1.0 is corrected only for errors that change a number; refills go to a later version (NTB-0009; IDEER.md).

**Retention limits for data about people.** Not applicable.

**Older versions.** The preregistration (`prereg-v1`) stays on Zenodo under its DOI. Nothing more is recorded.

**Mechanism for contributions.** Not recorded.

**Other comments.** None.
