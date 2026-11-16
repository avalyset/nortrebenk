# NTB-0002: Format, plattform og kjører

- Status: vedtatt 2026-11-16

## Kontekst

I P1 ble instansene skrevet som Multi-SWE-bench-definisjoner mot commit 24f493f og kjørt med en tynn kjører bygget på Multi-SWE-bench-klassene. Multi-SWE-bench sin egen kjøring brukte et image som bare fantes for linux/amd64, mens maskinen kjørte linux/arm64. P1 validerte derfor på linux/arm64.

## Beslutning

Instansene skrives som Multi-SWE-bench-definisjoner mot commit 24f493f. Kjøreren er den tynne kjøreren fra P1, bygget på Multi-SWE-bench-klassene. Plattformen for sett og måling avgjøres ved én avgrenset prøve i P2.2: kafka-manager (4 oppgaver) bygges og kjøres som linux/amd64 på Modal. Gir prøven de samme fail-to-pass- og pass-to-pass-listene som P1, er amd64 på Modal plattformen, og alle oppgavene valideres der. Ellers er plattformen linux/arm64 lokalt, og begrensningen står i README. Utfallet føres i NTB-0011. Uansett påstås det ikke at instansene er kjørt gjennom uendret Multi-SWE-bench.

## Alternativer vurdert

- Egen harness og eget format. Argument mot beslutningen: full kontroll og ingen avhengighet av en ekstern kodebase. Forkastet fordi et etablert format gjør instansene gjenbrukbare.
- Uendret Multi-SWE-bench på amd64 lokalt via emulering. Argument mot beslutningen: det ville gitt kjøring gjennom uendret harness. Forkastet fordi JVM- og Node-bygg under emulering ble vurdert som for trege, og fordi colima-konfigurasjonen ikke skulle endres.
- Hele valideringen direkte på Modal uten prøve. Argument mot beslutningen: sparer ett steg. Forkastet fordi en prøve på ett repo viser om plattformene gir samme testlister før all validering flyttes.

## Konsekvenser

P2.2 starter med prøven på kafka-manager. Plattformvalget føres i NTB-0011. README beskriver kjøreren som en tynn kjører på Multi-SWE-bench-klassene.

## Kilder

- SWE-bench-dokumentasjonen, «Evaluation – SWE-bench», seksjonen «Cloud-Based Evaluation» (swebench.com/SWE-bench/guides/evaluation/): «Run evaluation on Modal»
