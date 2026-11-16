# Avvik

Avvik fra planen føres her med dato og begrunnelse. Beslutninger tatt før forhåndsregistreringen står som ADR i `docs/decisions/` og er ikke avvik.

## 1. P1 kjørt på linux/arm64 med egen tynn kjører (2026-11-16)

Kjøringsvalideringen i P1 ble kjørt på linux/arm64 med en egen tynn kjører bygget på Multi-SWE-bench-klassene, ikke gjennom uendret Multi-SWE-bench. Multi-SWE-bench sin kjøring går via et image som bare finnes for linux/amd64. Se NTB-0002.

## 2. Regel for kjørefeil lagt til under P1 (2026-11-16)

Regelen «C uten testrapporter gir kjorefeil» (C = base + testpatch + gullpatch) ble lagt til under P1, etter første repo. Én kandidat ble omklassifisert fra «ingen_f2p» til «kjorefeil» ut fra de lagrede loggene, uten ny kjøring. Regelen endret ikke antall validerte.

## 3. Codex-armen utgikk (2026-11-16)

Codex-armen, som lå i den opprinnelige planen, utgikk fra v1.0 fordi studien gjennomføres uten utgifter utover eksisterende kreditt (NTB-0012).
