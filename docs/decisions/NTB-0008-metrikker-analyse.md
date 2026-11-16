# NTB-0008: Metrikker og analyse

- Status: vedtatt 2026-11-16
- Endret 2026-11-16: hovedmål og parvis sammenligning av tekstvarianter, se NTB-0013.

## Kontekst

Oppgavene kommer fra fem repoer, og oppgaver fra samme repo er ikke uavhengige. Settet er lite.

## Beslutning

Løst betyr at alle fail-to-pass- og pass-to-pass-tester passerer. Løst andel rapporteres per arm med intervall, både per oppgave og klynget på repo (5 klynger). Kostnad per løste oppgave er samlet kostnad for alle kjøringer, også mislykkede, delt på antall løste. Tid er veggklokke fra agentstart til levert patch, rapportert som median og kvartiler. Differanser mellom armer rapporteres parvis per oppgave med intervall, beskrivende. Det formuleres ingen bekreftende hypotese om hvem som er best, og det gjøres ingen sammenligning med menneskelig tidsbruk. Tekstspråk og agentmarkør rapporteres som beskrivende inndelinger.

## Alternativer vurdert

- Bekreftende test av forskjell mellom armer. Argument mot beslutningen: gir en klar konklusjon. Forkastet fordi settets størrelse og klyngingen gir lav styrke.
- Bare naive intervaller. Argument mot beslutningen: enklere. Forkastet fordi klynging på repo kan gi vesentlig bredere intervaller.

## Konsekvenser

Intervallene blir brede med fem klynger. Analysekoden låses i prereg-v1.

## Kilder

- Miller, «Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations», arXiv:2411.00640: «Conceptualizing evaluation questions as having been drawn from an unseen super-population»; og fra PDF-en: «Analyzing the same data, clustered standard errors can be over 3X larger than naive standard errors.»
