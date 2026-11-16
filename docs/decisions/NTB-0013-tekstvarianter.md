# NTB-0013: Tekstvarianter

- Status: vedtatt 2026-11-16
- Endret 2026-11-16: uavhengig kontroll av den utvidede teksten.

## Kontekst

Kvalitetssjekken i P2.3 lot 4 av 21 oppgaver bestå. 16 ble utelukket på kriteriet om at testene kan avvise gyldige løsninger, og én på begge kriteriene. Vurdererne begrunner utelukkelsene med at testene krever navn, filstier, nøkler eller strenger som ikke står i PR-teksten. Fire oppgaver, tre av dem fra samme repo, gir ingen måling. SWE-Bench Pro beholder underspesifiserte oppgaver og utvider oppgaveteksten med krav og grensesnitt som er forankret i testene.

## Beslutning

Hver oppgave får to tekstvarianter. «PR-tekst» er tittel og beskrivelse slik de står i instances.jsonl. «Utvidet» er PR-teksten med to tillegg etter mønsteret i SWE-Bench Pro: krav og grensesnitt. Kravene sier hvilken atferd fail-to-pass-testene kontrollerer og som PR-teksten ikke oppgir, med eksakte navn, nøkler og strenger der testene krever dem. Grensesnittet lister klasser, funksjoner, metoder og felt som testene bruker og som må opprettes eller endres, med filsti, inndata og utdata. Tilleggene inneholder ikke implementasjonskode og omtaler ikke testene eller gullpatchen. De skrives på engelsk av én modell (claude-opus-5-5) ut fra PR-tekst, gullpatch, testpatch og fail-to-pass-navn, med fast prompt, og kontrolleres mekanisk: ingen kodeblokker, ingen linje lik en tilføyd gullpatchlinje på minst 20 tegn, alle navn i grensesnittet finnes i testpatchen eller gullpatchen, og alle filstier finnes i gullpatchen. Feiler kontrollen, skrives tillegget én gang til; feiler det igjen, består ikke oppgaven.

Kvalitetskravet i NTB-0003 gjelder den utvidede teksten. Den vurderes med samme prompt, samme tre vurderere og samme regel som i P2.3. OpenAI-vurdereren kalles bare for oppgaver der stemmen kan endre utfallet, altså der nøyaktig én av de to andre stemmer for utelukkelse på et kriterium, fordi restkreditten ikke dekker alle. Mangler en slik stemme når kreditten er brukt, består ikke oppgaven. Grensen på 20 i NTB-0003 står.

I P3 kjøres begge tekstvarianter for oppgavene i settet. Hovedmålet er løst andel på utvidet tekst. Forskjellen mellom variantene rapporteres parvis per oppgave, beskrivende, og inndelt etter utfallet av kvalitetssjekken av PR-teksten i P2.3. Rekker ikke budsjettet, kuttes kjøringer før tekstvariant, og PR-tekst-varianten før en arm.

Uavhengig kontroll: OpenAI-vurdereren vurderer den utvidede teksten med samme prompt, for alle oppgavene i settet hvis restkreditten dekker det, ellers for 11 av de 17 som ble utelukket i P2.3, trukket med frø 20261116 fra sorterte ID-er. Stemmen endrer ikke settet, fordi regelen krever to stemmer. Oppgaver der den stemmer for utelukkelse, merkes, og hovedmålet rapporteres både med og uten dem.

## Alternativer vurdert

- Fryse settet med de fire som består med PR-teksten. Argument mot beslutningen: ingen endring etter at utfallet er kjent. Forkastet fordi fire oppgaver ikke gir en måling, og fordi litteraturen har en etablert måte å rette opp underspesifiserte oppgaver på.
- La mennesker skrive tilleggene, som i SWE-Bench Pro. Argument mot beslutningen: det er forbildet. Forkastet fordi forfatteren ikke er vurderer (NTB-0004), og studien har ingen andre annotatører.
- Kjøre bare PR-teksten på alle 21. Argument mot beslutningen: det er teksten etatene faktisk har. Forkastet som eneste variant fordi feil da ikke kan skilles fra tester som avviser gyldige løsninger; varianten kjøres som sammenligning.

## Konsekvenser

Endringen er gjort etter at utfallet av P2.3 og røykprøven var kjent, og før noen agentkjøring på oppgavene i settet. Den er tidsstemplet før tilleggene ble laget. Tilleggene er skrevet av en modell fra samme leverandør som agentene, uten menneskelig kontroll, og at en oppgave består, kan hvile på vurdereren fra samme leverandør. Tilleggene oppgir navn og strenger fra løsningen. Alt dette føres som grenser i README når repoets dokumenter skrives om i P2.5.

## Kilder

- Deng mfl., «SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?», arXiv:2509.16941v2, §3.2: «These requirements are grounded on the unit tests that are used for validation.»
- Samme, tillegg B.2: «Requirements never include specific code implementation and don’t leak solutions.»
- Samme, tabell 3 (løst andel med problembeskrivelse, krav og grensesnitt mot bare problembeskrivelse): OpenAI GPT-5 (high) 25.9% mot 8.40%; Claude Opus 4.1 22.7% mot 8.20%.
- OpenAI, «SWE-bench Annotation Instructions» (cdn.openai.com/introducing-swe-bench-verified/swe-b-annotation-instructions.pdf): «We find that the most common problems occur when there are subtle discrepancies between the tests and the issue text, such as the tests relying on a new function, variable name, or error message that were introduced in the Gold Patch but is not mentioned or differs from the Issue Description.»
