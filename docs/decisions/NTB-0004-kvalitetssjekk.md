# NTB-0004: Kvalitetssjekk

- Status: vedtatt 2026-11-16

## Kontekst

Oppgaveteksten er PR-beskrivelsen, som kan beskrive løsningen eller være for vag. Testene kan også avvise gyldige løsninger. SWE-bench Verified brukte menneskelige annotatorer med en rubrikk for disse forholdene.

## Beslutning

Hver oppgave vurderes etter de to kriteriene i SWE-bench Verified-rubrikken (underspesifisert oppgavetekst; tester som avviser gyldige løsninger), med skår 0–3, av tre modeller fra ulike leverandører med rubrikken som prompt. Flertall (≥ 2) for utelukkelse på ett kriterium gir utelukkelse. Ensemblet måles først mot de publiserte menneskelige Verified-annotasjonene. I tillegg føres to mekaniske felt per oppgave: andelen av gullpatchens tilføyde linjer som står ordrett i oppgaveteksten, og om testpatchen kompilerer mot base. Alle vurderinger publiseres. Forfatteren er ikke vurderer.

## Alternativer vurdert

- Forfatteren vurderer selv. Argument mot beslutningen: menneskelig vurdering er standarden i Verified. Forkastet fordi forfatteren kjenner oppgavene og utfallene fra P1.
- Ingen kvalitetssjekk. Argument mot beslutningen: færre steg og lavere kostnad. Forkastet fordi PR-beskrivelser kan inneholde løsningen.

## Konsekvenser

Kvalitetssjekken (P2.3) bruker API-kreditt. Ensemblets samsvar med de menneskelige annotasjonene rapporteres før det brukes på settet.

## Kilder

- OpenAI, «Introducing SWE-bench Verified», 13.08.2024 (openai.com/index/introducing-swe-bench-verified/): [U] siden ga HTTP 403 ved henting 16.11.2026; ikke sitert.
- OpenAI, 23.02.2026, oppgitt tittel «Why SWE-bench Verified no longer measures frontier coding capabilities»; siden ble funnet med tittelen «Why we no longer evaluate SWE-bench Verified» (openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/): [U] siden ga HTTP 403 ved henting 16.11.2026; ikke sitert.
- «SWE-rebench V2: Language-Agnostic SWE Task Collection at Scale», arXiv:2602.23866 (sammendraget; §3.4 lot seg ikke sitere ordrett fra PDF-teksten): «filters unsound instances using an ensemble of LLM judges, validated against human-verified SWE-bench annotations»
