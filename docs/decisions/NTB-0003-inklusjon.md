# NTB-0003: Inklusjon i settet

- Status: vedtatt 2026-11-16
- Endret 2026-11-16: kvalitetskravet gjelder utvidet oppgavetekst, se NTB-0013.

## Kontekst

P1 validerte 21 av 30 kandidater. Validering i P1 betydde minst én fail-to-pass-test og ingen test som passerte på base og feilet med gullpatch, i én kjøring på linux/arm64.

## Beslutning

En oppgave tas inn i settet når alle disse er oppfylt: den er P1-validert; den har et stabilt fail-to-pass-sett over tre kjøringer på plattformen fra NTB-0002; den bygger uten token; lisensen er MIT eller Apache-2.0; den er merget etter seneste treningsgrense blant modellene som måles; den finnes ikke i Multi-SWE-bench eller SWE-rebench V2; og den består kvalitetssjekken (NTB-0004). Basis er base_sha slik den ble validert. Kandidater som ikke ble validert i P1, tas ikke inn. Antallet som står igjen, er et resultat. Står færre enn 20 igjen, publiseres v1.0 som metode og gjennomførbarhetsfunn uten at kravene senkes.

## Alternativer vurdert

- Ta inn ikke-validerte kandidater etter manuell retting (f.eks. merge-forelder som basis). Argument mot beslutningen: flere oppgaver. Forkastet fordi rettinger etter at resultatet er kjent, gjør utvalget avhengig av utfallet; ideen står i IDEER.md.
- Senke kravene hvis færre enn 20 står igjen. Argument mot beslutningen: settet ville blitt større. Forkastet fordi kravene da ville blitt satt etter data.

## Konsekvenser

Settets størrelse er ukjent til P2.2–P2.3 er ferdige. Treningsgrensene for alle modeller må fastsettes før inklusjon.

## Kilder

- «SWE-rebench: An Automated Pipeline for Task Collection and Decontaminated Evaluation of Software Engineering Agents», arXiv:2505.20411: «show that performance of some language models might be inflated due to contamination issues»
