# NTB-0004: Kvalitetssjekk

- Status: vedtatt 2026-11-16
- Endret 2026-11-16: skårgrense og sammenslåingsregel presisert.

## Kontekst

Oppgaveteksten er PR-beskrivelsen, som kan beskrive løsningen eller være for vag. Testene kan også avvise gyldige løsninger. SWE-bench Verified brukte menneskelige annotatorer med en rubrikk for disse forholdene.

## Beslutning

Hver oppgave vurderes etter de to kriteriene i SWE-bench Verified-rubrikken (underspesifisert oppgavetekst; tester som avviser gyldige løsninger), med skår 0–3, av tre modeller fra ulike leverandører med rubrikken som prompt. En modell stemmer for utelukkelse på et kriterium når den gir skår 2 eller 3. Sammenslåingsregelen velges på ankerutvalget fra de menneskelige Verified-annotasjonene, før den brukes på egne oppgaver: enten utelukkes en oppgave når minst én av tre modeller stemmer for utelukkelse på et kriterium, eller når minst to av tre gjør det. Regelen med høyest samsvar med de menneskelige annotasjonene velges; ved likt samsvar velges den strengeste. Ensemblet måles først mot de publiserte menneskelige Verified-annotasjonene. I tillegg føres to mekaniske felt per oppgave: andelen av gullpatchens tilføyde linjer som står ordrett i oppgaveteksten, og om testpatchen kompilerer mot base. Alle vurderinger publiseres. Forfatteren er ikke vurderer.

## Alternativer vurdert

- Forfatteren vurderer selv. Argument mot beslutningen: menneskelig vurdering er standarden i Verified. Forkastet fordi forfatteren kjenner oppgavene og utfallene fra P1.
- Ingen kvalitetssjekk. Argument mot beslutningen: færre steg og lavere kostnad. Forkastet fordi PR-beskrivelser kan inneholde løsningen.

## Konsekvenser

Kvalitetssjekken (P2.3) bruker API-kreditt. Ensemblets samsvar med de menneskelige annotasjonene rapporteres før det brukes på settet.

## Kilder

- OpenAI, «Introducing SWE-bench Verified», 13.08.2024 (openai.com/index/introducing-swe-bench-verified/), lest i nettleser 16.11.2026. Utelukkelse ved samlet skår 2 eller høyere: «have an ensemble label of 2 or above in severity»; sammenslåing: «taking the highest-severity label amongst the 3 annotators». Siden har ingen enkeltsetning som sier begge deler; de to delene står i hver sin setning.
- OpenAI, «Why SWE-bench Verified no longer measures frontier coding capabilities» (sidetittel «Why we no longer evaluate SWE-bench Verified»), 23.02.2026 (openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/), lest i nettleser 16.11.2026: «This is why we have stopped reporting SWE-bench Verified scores»
- «SWE-rebench V2: Language-Agnostic SWE Task Collection at Scale», arXiv:2602.23866 (sammendraget; §3.4 lot seg ikke sitere ordrett fra PDF-teksten): «filters unsound instances using an ensemble of LLM judges, validated against human-verified SWE-bench annotations»
