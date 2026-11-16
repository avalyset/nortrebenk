# NTB-0005: Agentspor

- Status: vedtatt 2026-11-16

## Kontekst

Forhåndsfaktaene fra P1 merket agentmarkør ja når PR-tekst eller commit-meldinger hadde eksplisitt spor (f.eks. «Co-authored-by: Copilot» eller «Generated with Claude Code»). 3 av de 21 validerte oppgavene hadde markør.

## Beslutning

Hver oppgave merkes med agentmarkør ja eller nei ut fra PR-tekst og commit-meldinger. Oppgavene beholdes, og resultatet rapporteres også delt på merket. Fravær av markør betyr ikke at koden er menneskeskrevet.

## Alternativer vurdert

- Utelukke oppgaver med markør. Argument mot beslutningen: oppgaver løst med agent kan være lettere for agenter. Forkastet fordi markøren bare fanger eksplisitte spor, så utelukkelse ville gitt en falsk skillelinje.

## Konsekvenser

Rapporten viser resultater for alle oppgaver og delt på markør. Markøren beskriver bare synlige spor.

## Kilder

- Ingen ekstern kilde; beslutningen hviler på forhåndsfaktaene fra P1.
