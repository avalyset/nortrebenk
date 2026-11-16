# Avvik

Avvik fra planen føres her med dato og begrunnelse. Beslutninger tatt før forhåndsregistreringen står som ADR i `docs/decisions/` og er ikke avvik.

## 1. P1 kjørt på linux/arm64 med egen tynn kjører (2026-11-16)

Kjøringsvalideringen i P1 ble kjørt på linux/arm64 med en egen tynn kjører bygget på Multi-SWE-bench-klassene, ikke gjennom uendret Multi-SWE-bench. Multi-SWE-bench sin kjøring går via et image som bare finnes for linux/amd64. Se NTB-0002.

## 2. Regel for kjørefeil lagt til under P1 (2026-11-16)

Regelen «C uten testrapporter gir kjorefeil» (C = base + testpatch + gullpatch) ble lagt til under P1, etter første repo. Én kandidat ble omklassifisert fra «ingen_f2p» til «kjorefeil» ut fra de lagrede loggene, uten ny kjøring. Regelen endret ikke antall validerte.

## 3. Codex-armen utgikk (2026-11-16)

Codex-armen, som lå i den opprinnelige planen, utgikk fra v1.0 fordi studien gjennomføres uten utgifter utover eksisterende kreditt (NTB-0012).

## 4. Google-vurdereren bare på gratisnivå (2026-11-16)

NTB-0004 krever én vurderer fra Google. Gemini-nøkkelens prosjekt er på gratisnivå (Google AI Studio, 16.11.2026), og studien skal ikke ha utgifter utover eksisterende kreditt (NTB-0012). Den sterkeste gratismodellen med dagskvote for alle 121 kall, gemini-3.5-flash-lite, ble brukt. Den er ikke leverandørens sterkeste modell.

## 5. Kjørerankeret mot Multi-SWE-bench falt bort (2026-11-16)

Kjøreren skulle ankres mot de publiserte testlistene for Altinn/app-frontend-react i Multi-SWE-bench. Datasettet (ByteDance-Seed/Multi-SWE-bench) har ingen instanser for repoet, og det har heller ikke Multi-SWE-RL, Multi-SWE-bench_mini eller Multi-SWE-bench-flash. Sammenligningen kunne ikke gjøres. Se `data/anker/msb_altinn.md`. Kjøreren kontrolleres i stedet mot uendret Multi-SWE-bench-harness i krysskontrollen på amd64 i P4 (NTB-0011).

## 6. Røykprøvesøket bygde under diskgrensen (2026-11-16)

Grensen for P2.4 var minst 6 GiB ledig på disken før hvert bygg. Søket etter røykprøveoppgave i navikt/mock-oauth2-server (C1) startet bygget med 5 GiB ledig, fordi søkeskriptet ikke målte disken før hvert bygg. Bygget og kjøringene ga ingen diskfeil. Senere bygg ble målt på forhånd og stoppet under grensen.

## 7. Nytt steg P2.3b og to tekstvarianter (2026-11-16)

Kartet hadde ikke steget. Det er lagt inn etter at P2.3 lot 4 av 21 oppgaver bestå. Kvalitetskravet gjelder nå utvidet tekst, og P3 kjører to tekstvarianter (NTB-0013). Endringen er gjort før noen agentkjøring på oppgavene i settet.
