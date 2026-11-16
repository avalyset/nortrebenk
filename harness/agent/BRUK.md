# Agentkjøring (NTB-0006, NTB-0007)

Claude Code kjøres som agent i en container uten rute ut. Eneste vei ut er en mellomtjener som videresender til modell-API-et.

## Innhold

- `agentbilde.py`: byggoppskrift for agentbildet.
  - Samme festede base-image, oppsett, installasjon og oppvarming som instansbildet i `harness/msb_repos/`.
  - Bildet har ikke gullpatch, testpatch eller kjøreskript.
  - Repoet, git-forseglingen og avhengighetscachen eies av brukeren `agent`. Claude Code nekter `--dangerously-skip-permissions` som root.
  - Claude Code er lagt inn som selvstendig binærfil, festet til en versjon (`CC_VERSJON`) og kontrollert mot sha256 fra versjonens manifest.
  - Miljøet peker mot mellomtjeneren, har en plassholder som nøkkel og slår av telemetri, feilrapportering, oppdateringer og annen ikke-nødvendig trafikk.
- `mellomtjener.py`: videresender bare stier under `/v1/` til api.anthropic.com, med strømming.
  - Nøkkelen leses fra miljøvariabelen `NTB_UPSTREAM_KEY` og settes som `x-api-key`. Innkommende nøkkelhoder fjernes.
  - Kall med tjenersideverktøy for nettsøk eller netthenting avvises med 400, og andre stier med 403.
  - Loggen har tid, metode, sti, status og om kallet ble avvist, aldri innhold eller hoder.
- `selvtest.sh`: selvtest uten modellkall. Den kjøres i en fersk container før hver agentkjøring og kontrollerer fem ting:
  - at ingen filer heter `fix.patch`, `test.patch`, `run-B.sh` eller `run-C.sh`;
  - at gullpatchens tre lengste tilføyde linjer ikke finnes under `/home`, `/root` eller `/tmp`;
  - at github.com og pakkeregistrene ikke kan nås;
  - at miljøet ikke har noen nøkkel;
  - at git har én commit, ingen remotes og én ref.
- `kjor_agent.py`: nett og mellomtjener, bygg, selvtest (også med modellkall), kontroll av vurderingsveien, agentkjøring og vurdering.
- `innpakning.txt`: den faste innpakningen av oppgavens tittel og beskrivelse, lik for alle oppgaver og armer.
- `budsjett.py`: lager `data/roykprove/kjoringer.jsonl` og `budsjett.md` fra kjøringsfilene.

## Kjøring

Krav: Docker og Python med multi-swe-bench (commit 24f493f) og Docker-SDK for Python. Stiene settes med miljøvariabler:

- `NTB_MSB_REPOS`: repo-definisjonene, `harness/msb_repos`.
- `NTB_OPPGAVER`: mappe med `<org>__<repo>__<pr>.json`, med feltene `org`, `repo`, `pr`, `url`, `basis_sha`, `tittel` og `beskrivelse`.
- `NTB_PATCHER`: mappe med `<org>__<repo>__<pr>/test.patch` og `fix.patch`.
- `NTB_TESTER`: mappe med `<org>__<repo>__<pr>.json`, med listene `f2p` og `p2p`.
- `NTB_UT`: logger, transkripter, patcher og resultater.

```bash
python harness/agent/kjor_agent.py nett                         # internt nett ntb-agent og mellomtjener
python harness/agent/kjor_agent.py bygg <id>                     # agentbilde
python harness/agent/kjor_agent.py selvtest <id> --modell        # selvtest med de to modellkallene
python harness/agent/kjor_agent.py kontroll <id>                 # gullpatch utenom test gir løst, tom patch ikke
python harness/agent/kjor_agent.py kjor <id> claude-sonnet-5-5 1.50
```

`nett` leser nøkkelen fra `ANTHROPIC_API_KEY_NORDVAULT` i prosessmiljøet. Nøkkelen gis til mellomtjeneren med `docker run -e NTB_UPSTREAM_KEY` uten verdi, så den aldri står på en kommandolinje og aldri finnes i agentcontaineren.

En kjøring gjør dette:
1. Selvtesten kjøres først. Feiler den, kjøres ikke agenten.
2. Agenten kjøres med `claude -p`, `--output-format stream-json --verbose`, `--dangerously-skip-permissions`, `--disallowedTools WebSearch WebFetch` og `--max-budget-usd`. Kjøreren har en tidsgrense på 40 minutter.
3. Patchen er alle endringer mot den ene commiten. Filer oppvarmingen laget før agenten startet, er holdt utenfor.
4. Endringer i filer som testpatchen berører, forkastes.
5. Patchen vurderes i en fersk container fra instansbildet uten nett: base, agentpatch og testpatch. Oppgaven er løst når alle f2p- og p2p-tester består.
