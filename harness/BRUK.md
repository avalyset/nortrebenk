# Bruk av harnessen (P2.2)

Harnessen bygger ett forseglet Docker-image per oppgave og kjører oppgavens tester i nye containere. Den bruker klassene i Multi-SWE-bench (commit 24f493f): `PullRequest`, `Config`, `Image` og `Instance`. Kjøringen går gjennom en egen, tynn kjører, fordi Multi-SWE-bench sin testkjøring (swe-rex og `nix_swe`) bare finnes for linux/amd64. P2.2 er kjørt på linux/arm64.

## Innhold

- `msb_repos/_felles.py`: felles kode. Bygger det forseglede imaget, lager kjøreskriptene og leser JUnit-XML og TRX.
- `msb_repos/<org>/<repo>.py`: én definisjon per repo. Base-imaget er festet med digest. Definisjonen har oppsett, installasjon, oppvarming og testkommando.
- `scripts/p22_kjor.py`: kjører alle oppgaver i ett repo.

## Forseglet image

1. Repoet klones i et eget byggesteg og sjekkes ut på `base_sha`. Mappa `.git` slettes.
2. Arbeidstreet kopieres inn i det endelige imaget, som får et nytt git-repo med én commit. Det har ingen remotes og ingen andre refs.
3. Avhengighetene installeres etter forseglingen. Oppvarmingen kjører testene én gang, slik at byggverktøyets cache er fylt.
4. Imaget kontrollerer selv at `git log --all` gir én commit, at `git remote -v` er tom og at det bare finnes én ref. Først da skrives `/home/forsegling.txt`.

Kjøringene bruker ikke `git fetch` eller `git clean -x`.

## Kjøringer

- **B**: testpatchen legges på base. Kjøres én gang, med nett.
- **C**: testpatchen og gullpatchen legges på base. Kjøres tre ganger, hver gang i en ny container. Første C kjøres med `--network none`. Feiler den på grunn av nett, settes `trenger_nett_i_test: true`, og alle tre C kjøres med nett.

En oppgave er løst når alle tester i P1-listene `f2p` og `p2p` har PASS.

Oppgaven tas med i settet (`i_settet_etter_p22: ja`) når fire vilkår er oppfylt:
- B er ikke løst.
- C er løst i alle tre kjøringene.
- Kjøringen ble fullført.
- Forseglingen er kontrollert.

## Kjøre

Krav:
- Docker
- Python 3.12 med multi-swe-bench (commit 24f493f, `uv pip install -e .`) og `docker` (Python-SDK)

Kjøreren leser tre stier fra miljøvariabler:

- `NTB_P1`: mappe med `results.jsonl` (P1-status per oppgave; oppgaver med `status: validert` kjøres), `c2_patcher.jsonl` (én linje per oppgave med `url`, `repo`, `pr`, `basis_sha` og `deps_reinstall`) og `tester/<org>__<repo>__<pr>.json` (lister `f2p` og `p2p`). `data/p1_resultater.jsonl` og `data/tester/` i dette repoet har det samme innholdet.
- `NTB_PATCHER`: mappe med `<org>__<repo>__<pr>/test.patch` og `fix.patch`. Patchene for oppgavene i settet ligger i `data/instances.jsonl` (feltene `testpatch` og `gullpatch`).
- `NTB_UT`: mappe for logger, byggmapper og resultater (standard `ntb-ut`).

```bash
NTB_P1=... NTB_PATCHER=... NTB_UT=ntb-ut python harness/scripts/p22_kjor.py navikt/mock-oauth2-server 2
```

Siste argument er antall oppgaver som kjøres parallelt (standard 2). Hver oppgave har en tidsgrense på 40 minutter. Resultatet for hver oppgave skrives til `$NTB_UT/res/<org>__<repo>__<pr>.json`, og loggene til `$NTB_UT/logs/<org>__<repo>__<pr>/`.

Ved importfeil på macOS: multi-swe-bench 24f493f har både `repos/python/Qiskit` og `repos/python/qiskit`, som kolliderer på filsystemer som ikke skiller mellom store og små bokstaver. Kjøreren erstatter derfor den samlede repo-importen med en tom modul.
