# NTB-0007: Agenter, modeller og betaling

- Status: vedtatt 2026-11-16
- Arm 3 utgår fra v1.0, se NTB-0012.
- Endret 2026-11-16 (2): innpakning, versjon og kjørerekkefølge.

## Kontekst

Studien skal oppgi kostnad per løste oppgave. Kostnaden må måles per kall og være skilt fra abonnementer.

## Beslutning

Det kjøres tre armer i prioritert rekkefølge: Claude Code med Opus 5.5, Claude Code med Sonnet 5.5, og Codex med gjeldende toppmodell (modell-ID festes i P2.4, [U] til da). Det kjøres tre kjøringer per arm og oppgave. Claude-armene kjøres først og belastes Anthropic-API-et, ikke Max-abonnementet, slik at kostnaden kan måles; Codex belastes OpenAI-API-et. Rekker ikke budsjettaket, kuttes kjøringer før armer, og arm 3 før arm 2. Agentene kjøres med standardinnstillinger og uten egen promptjustering. Tidsgrense, kostnadstak per oppgave og samlet budsjettak settes fra P2.4. Ingen kjøring legges til for å bruke opp kreditt.

Agenten får oppgavens tittel og beskrivelse i en fast innpakning (harness/agent/innpakning.txt), lik for alle oppgaver og armer. Claude Code-versjonen festes og føres. Kjøringene går én om gangen. Tak per kjøring settes med agentens egen budsjettgrense og en tidsgrense i kjøreren. Eneste avvik fra standardinnstillingene er det forseglingen krever (NTB-0006). Agentoppsettet ankres ikke mot publiserte løsningsrater i v1.0, fordi kreditten ikke dekker et utvalg som er stort nok til å sammenligne rater.

## Alternativer vurdert

- GitHub Copilot som arm. Argument mot beslutningen: det er verktøyet etatene betaler for. Forkastet i v1.0 fordi kostnad per kall ikke kan måles på samme måte; ideen står i IDEER.md.
- Én kjøring per arm og oppgave. Argument mot beslutningen: lavere kostnad. Forkastet fordi variasjon mellom kjøringer da ikke kan anslås.

## Konsekvenser

Kostnad rapporteres fra API-faktureringen. Armrekkefølgen bestemmer hva som kuttes ved budsjettmangel.

## Kilder

- Kapoor mfl., «AI Agents That Matter», arXiv:2407.01502: «Our focus on cost in addition to accuracy motivates the new goal of jointly optimizing the two metrics.»
