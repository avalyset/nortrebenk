# NTB-0006: Forsegling

- Status: vedtatt 2026-11-16

## Kontekst

Oppgavene er hentet fra offentlige repoer der løsningen finnes i senere commits og på nett. Agenter kan slå opp løsningen i stedet for å utlede den.

## Beslutning

Instansbildet har repoet på base_sha uten senere git-objekter, uten remotes og uten refs. Agentens nett er begrenset til modell-API og pakkeregistre; github.com er sperret. Avhengighetene er løst i bildet. Kjøres agentene på Modal, ligger API-nøkkelen som Modal-hemmelighet, som en egen nøkkel med beløpsgrense som slettes etter P3.

## Alternativer vurdert

- Full nettilgang. Argument mot beslutningen: agentene får samme vilkår som i vanlig bruk. Forkastet fordi fasiten da er ett oppslag unna.
- Ingen nettilgang. Argument mot beslutningen: sterkest forsegling. Forkastet fordi agentene trenger modell-API-et.

## Konsekvenser

Bildet må bygges med avhengigheter på forhånd. Nettregler og nøkkelhåndtering dokumenteres i harness/.

## Kilder

- Cursor, «Reward hacking is swamping model intelligence gains» (cursor.com/blog/reward-hacking-coding-benchmarks): «If the agent has access to repository history or the public web, it can sometimes look up the answer rather than derive it.»
- NIST CAISI, «Cheating On AI Agent Evaluations» (nist.gov/blogs/caissi-research-blog/cheating-ai-agent-evaluations): «Models cheating on coding benchmarks by looking up more recent code versions, disabling assertions, and adding test-specific logic.»
- «SWE-Lego: Pushing the Limits of Supervised Fine-tuning for Software Issue Resolving», arXiv:2601.01426: «the agent sometimes peeked at Git history or future commits, thereby cheating rather than faithfully resolving the issue.»
- Modal-dokumentasjonen, «Networking and security» (modal.com/docs/guide/sandbox-networking): «By default, Sandboxes can make outbound connections to any public IP address.»
