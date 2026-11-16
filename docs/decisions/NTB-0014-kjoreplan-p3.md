# NTB-0014: Kjøreplan for P3

- Status: vedtatt 2026-11-16

## Kontekst

P3 skal kjøre oppgavene i settet med to armer, to tekstvarianter og tre kjøringer (NTB-0007, NTB-0013). Disken rommer ikke bilder for alle oppgavene samtidig, og kreditten har et tak (NTB-0012). Røykprøven målte høyst 9,43 USD for én runde over 21 oppgaver og to armer. Vurderingsveien i agentkjøreren er en annen kodevei enn valideringen i P2.2, og to oppgaver trenger et eget bygg for å kjøre testene uten nett.

## Beslutning

P3 kjøres i inntil tre pass. Ett pass er én kjøring per oppgave, arm og tekstvariant, altså 84 kjøringer for 21 oppgaver. Innen et pass tas oppgavene i en rekkefølge stokket med frø 20261116 pluss passnummeret. For hver oppgave bygges instansbildet og agentbildet, selvtesten kjøres, vurderingsveien kontrolleres uten modellkall (gullpatchen utenom testfiler gir løst, tom patch gir ikke løst), de fire kjøringene gjøres i en rekkefølge gitt av samme frø, og bildene slettes. Kjøringene går én om gangen. Planen med alle kjøringene i rekkefølge lages av kjøreren før frys og ligger i data/p3_plan.jsonl.

Tak per kjøring er 1,50 USD for Sonnet 5.5 og 3,00 USD for Opus 5.5, satt med agentens budsjettgrense, og 40 minutter. En kjøring som treffer et tak, teller som ikke løst, og kostnad og tid telles med.

Budsjettet B er Anthropic-saldoen avlest rett før P3 minus 5,00 USD. Brukt beløp er summen for alle kjøringer, også forkastede forsøk. Første pass startes bare hvis B er minst 28,29 USD (1,5 ganger to runder à 9,43 USD). Et nytt fullt pass startes bare hvis det som står igjen av B, er minst 1,5 ganger kostnaden for det dyreste fullførte passet. Holder det ikke til et fullt pass, kjøres et pass med bare utvidet tekst hvis det som står igjen, er minst 1,5 ganger kostnaden for utvidet-delen av det dyreste passet. Ellers stopper P3. Inne i et pass startes ingen kjøring hvis brukt beløp pluss kjøringens tak overstiger B.

En infrastrukturfeil i en kjøring er at Claude Code avslutter med API-feil, eller at containeren stopper uten resultatlinje og uten at et tak slo inn. Kjøringen forkastes da og kjøres på nytt, høyst to ganger. Feiler den tredje gang, står den som manglende og teller ikke som ikke løst. Feiler bygget, selvtesten eller kontrollen av vurderingsveien for en oppgave etter to forsøk, står alle oppgavens kjøringer i passet som manglende. Forkastede forsøk, manglende kjøringer og kostnaden for dem rapporteres.

Et pass er fullført når hver planlagte kjøring enten er gjennomført eller står som manglende etter reglene over. Et pass som stoppes av budsjettet, er ufullstendig. Bare fullførte pass inngår i hovedanalysen, og ufullstendige rapporteres for seg.

Kjøreren for P3 nekter å kjøre agenter på oppgaver i settet før PREREG_DOI.txt finnes i repoet.

## Alternativer vurdert

- Alle tolv kjøringer per oppgave i ett bygg. Argument mot beslutningen: færre bygg. Forkastet fordi et budsjett som tar slutt underveis, da gir noen oppgaver alle kjøringer og andre ingen.
- Beholde alle bildene gjennom hele P3. Forkastet fordi disken ikke rommer dem.
- Kontrollere vurderingsveien bare før frys. Argument mot beslutningen: kortere pass. Forkastet fordi bygg kan endre seg mellom frys og kjøring, og en feil i vurderingsveien ellers ville stått som ikke løst.

## Konsekvenser

P3 tar tre pass med bygg og kontroll for hver oppgave i hvert pass. Rekkefølgen er fast og publisert før første kjøring.

## Kilder

- data/roykprove/budsjett.md; ingen ekstern kilde.
