# NTB-0001: Omfang, nytte og grenser

- Status: vedtatt 2026-11-16

## Kontekst

Kjøringsvalideringen (P1) ble avsluttet 16.11.2026: 21 av 30 kandidater ble validert på 5 repoer, fra to etater (Nav 13, Digdir/Altinn 8), med repo-språk Kotlin 13 og TypeScript 8. De validerte PR-ene ble merget mellom 02.11.2026 og 14.11.2026. Oppgaveteksten (PR-beskrivelsen) var engelsk i 13, norsk i 5 og blandet i 3.

## Beslutning

Formålet ble fastsatt som å måle hvor godt og raskt kodeagenter løser oppgaver fra offentlig kode i norske etater, og hva hver løste oppgave koster, med etatens egne tester som fasit. Brukerne er teknologiledelse i etatene (modellklasse under kostnadstak), DFD/Digdir/DFØ (gevinstmåling uten selvrapportering) og forskere på utviklerproduktivitet. v1.0 ble definert som et oppgavesett, en gjentakbar metode og en forhåndsregistrert pilotmåling. Det ble bestemt at v1.0 ikke er en rangering av agenter, ikke et bilde av etatenes kode, ikke et mål på lisensverdi, ikke en måling av menneske med agent og ikke en måling av GitHub Copilot. «Første norske» brukes ikke som hovedpåstand.

## Alternativer vurdert

- Bredere omfang (flere etater, alle språk, klasse B-repoer). Argument mot beslutningen: et bredere sett ville gi bedre dekning av etatenes kode. Forkastet fordi kjørbarheten bare er vist for de 21 oppgavene, og fordi flere repoer krever tjenester eller token (se IDEER.md).
- «Første norske benchmark» som hovedpåstand. Argument mot beslutningen: påstanden er enkel å formidle. Forkastet fordi tidligere arbeid finnes på nabofelt (se Kilder), og fordi en førstehetspåstand ikke kan etterprøves fullt ut.

## Konsekvenser

Resultatene gjelder bare oppgavene i settet. Dekningen er to etater, fem repoer og to repo-språk. Relatert arbeid nevnes i README og datablad: aktivitetsmåling av Copilot i Nav IT, britisk forsøk med kodeassistenter i offentlig sektor, ikke-engelsk oppgavetekst på repo-nivå og Multi-SWE-bench, som har en Altinn-repo (Altinn/app-frontend-react).

## Kilder

- Stray mfl., «Developer Productivity With and Without GitHub Copilot: A Longitudinal Mixed-Methods Case Study», arXiv:2509.20353: «We conducted a mixed-methods case study in NAV IT, a large public sector agile organization.»
- Government Digital Service, «AI coding assistant trial», gov.uk, publisert 12.09.2025: «The trial aimed to understand how these tools could help public sector engineering and development teams work better and be more productive.»
- «RuBench: A Repository-Level Agentic Coding Benchmark with Natively Authored Russian Task Specifications», arXiv:2607.06411: «each specified natively in Russian -- written from scratch, not translated»
- «Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving», arXiv:2504.02605: «we introduce a multilingual issue-resolving benchmark, called Multi-SWE-bench, covering Java, TypeScript, JavaScript, Go, Rust, C, and C++»
