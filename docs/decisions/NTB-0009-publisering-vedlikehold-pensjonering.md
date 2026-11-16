# NTB-0009: Publisering, vedlikehold og pensjonering

- Status: vedtatt 2026-11-16

## Kontekst

Settet består av ferske oppgaver fra offentlige repoer. Det blir kontaminert når nyere modeller trenes på data etter merge-datoene.

## Beslutning

Fulle instanser publiseres med kanaristreng og lisensangivelse per repo. v1.0 rettes bare ved feil som endrer et tall. Settet er gyldig for modeller med treningsgrense før den tidligste merge-datoen i det endelige settet; for nyere modeller er det pensjonert, og datoen står i README. Ferdig-kriteriene ved P4 er Agentic Benchmark Checklist, BetterBench og JOSS-sjekklisten. Databladet skrives etter Datasheets for Datasets.

## Alternativer vurdert

- Løpende oppdatering av v1.0. Argument mot beslutningen: settet holdes ferskt. Forkastet fordi publiserte tall da endres; påfyll står i IDEER.md som v1.1.

## Konsekvenser

README får en pensjoneringsdato. Frysen i P4 vurderes mot de tre sjekklistene.

## Kilder

- «Establishing Best Practices for Building Rigorous Agentic Benchmarks» (Agentic Benchmark Checklist), arXiv:2507.02825: «we show that many agentic benchmarks have issues in task setup or reward design.»
- «BetterBench: Assessing AI Benchmarks, Uncovering Issues, and Establishing Best Practices», arXiv:2411.12990: «we develop an assessment framework considering 46 best practices across an AI benchmark's lifecycle»
- «Datasheets for Datasets», arXiv:1803.09010 (identifikatoren kontrollert mot tittelen på arXiv-siden): «we propose that every dataset be accompanied with a datasheet that documents its motivation, composition, collection process, recommended uses, and so on.»
- JOSS-sjekklisten: ikke hentet i P2.1.
