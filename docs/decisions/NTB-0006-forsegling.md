# NTB-0006: Forsegling

- Status: vedtatt 2026-11-16
- Endret 2026-11-16: nettregel, nettverktøy, agentbilde og nøkkelhåndtering for lokal kjøring.

## Kontekst

Oppgavene er hentet fra offentlige repoer der løsningen finnes i senere commits og på nett. Agenter kan slå opp løsningen i stedet for å utlede den.

## Beslutning

Instansbildet har repoet på base_sha uten senere git-objekter, uten remotes og uten refs. Agentens nett er begrenset til modell-API og pakkeregistre; github.com er sperret. Avhengighetene er løst i bildet. Kjøres agentene på Modal, ligger API-nøkkelen som Modal-hemmelighet, som en egen nøkkel med beløpsgrense som slettes etter P3.

Agentens nett er begrenset til modell-API-et. Agentcontaineren står på et internt Docker-nett uten rute ut. Eneste vei ut er en mellomtjener som bare videresender til modell-API-et og legger på API-nøkkelen, slik at nøkkelen aldri finnes i agentcontaineren. Pakkeregistre og github.com er ikke tilgjengelige. Verktøy som lar modell-API-et søke eller hente på nettet på agentens vegne, er slått av i agenten og avvises i mellomtjeneren. Agentbildet bygges uten gullpatch, testpatch og kjøreskript, og det kontrolleres før hver kjøring. Avhengighetene for base og for tilstanden med gullpatch er løst i bildet, uten at kildeendringer fra gullpatchen følger med. Oppgaver der testene likevel ikke lar seg kjøre uten nett, merkes og rapporteres for seg. Setningene om pakkeregistre og om Modal over gjelder ikke lenger (NTB-0011).

## Alternativer vurdert

- Full nettilgang. Argument mot beslutningen: agentene får samme vilkår som i vanlig bruk. Forkastet fordi fasiten da er ett oppslag unna.
- Ingen nettilgang. Argument mot beslutningen: sterkest forsegling. Forkastet fordi agentene trenger modell-API-et.
- Pakkeregistre åpne. Argument mot beslutningen: agenten kan legge til avhengigheter slik en utvikler ville. Forkastet fordi et repo som publiseres som pakke, kan ha løsningen i en nyere pakkeversjon, og fordi 19 av 21 oppgaver kjører testene uten nett.

## Konsekvenser

Bildet må bygges med avhengigheter på forhånd. Nettregler og nøkkelhåndtering dokumenteres i harness/.

## Kilder

- Cursor, «Reward hacking is swamping model intelligence gains» (cursor.com/blog/reward-hacking-coding-benchmarks): «If the agent has access to repository history or the public web, it can sometimes look up the answer rather than derive it.»
- NIST CAISI, «Cheating On AI Agent Evaluations» (nist.gov/blogs/caissi-research-blog/cheating-ai-agent-evaluations): «Models cheating on coding benchmarks by looking up more recent code versions, disabling assertions, and adding test-specific logic.»
- «SWE-Lego: Pushing the Limits of Supervised Fine-tuning for Software Issue Resolving», arXiv:2601.01426: «the agent sometimes peeked at Git history or future commits, thereby cheating rather than faithfully resolving the issue.»
- Modal-dokumentasjonen, «Networking and security» (modal.com/docs/guide/sandbox-networking): «By default, Sandboxes can make outbound connections to any public IP address.»
