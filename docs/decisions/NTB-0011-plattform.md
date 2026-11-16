# NTB-0011: Plattform

- Status: vedtatt 2026-11-16

## Kontekst

Validering og måling skal skje på samme plattform. P1 validerte oppgavene på linux/arm64. Den inkluderte Modal-kreditten for november dekket ikke agentkjøringer.

## Beslutning

Måleplattformen for sett og pilotmåling er linux/arm64 lokalt, samme miljø som P1. Prøven på Modal som NTB-0002 beskrev, ble ikke kjørt. Før v1.0 kjøres gullpatch og tom patch for alle oppgavene i settet én gang på linux/amd64 som krysskontroll, bare hvis det kan gjøres på inkludert kreditt. Oppgaver som ikke gir samme utfall der, merkes i datasettet og i README, og måleresultatene endres ikke. NTB-0002 står ellers ved lag.

## Alternativer vurdert

- Alt på amd64 på Modal. Argument mot beslutningen: lettere å gjenskape for andre. Forkastet fordi validering og måling skal skje på samme plattform, og fordi den inkluderte Modal-kreditten for november ikke dekket agentkjøringer.
- Betalt Modal-bruk. Forkastet, se NTB-0012.

## Konsekvenser

Settet bygges og måles på linux/arm64. README oppgir plattformen. Krysskontrollen på amd64 gjøres bare hvis inkludert kreditt dekker den.

## Kilder

- Ingen ekstern kilde; beslutningen hviler på P1-protokollen og NTB-0002.
