# Frys-lesing runde 1 (v1.0), 2026-11-18, HEAD 5c8a042 (med OTS-statusen i hodet på RESULTATER.md uncommittet)

Uavhengig Opus-subagent, kun fillister og instruks. 6 funn: (a) 1, (b) 0, (c) 1, (d) 1, (e) 1, (f) 1, (g) 0, (h) 1. Etter regelen for frysen av v1.0 rettes bare foreldet status (e), metadata som motsier innholdet (f) og stier eller lenker som ikke finnes (g), og bare i README.md, RESULTATER.md, AVVIK.md nr. 9–12, IDEER.md, LICENSE, CITATION.cff, .zenodo.json, docs/DATASHEET.md, docs/ABC_CHECKLIST.md og analysis/lag_resultater.py; i PLAN.md bare lenker. Funn i klasse (a), (b) og (h) rettes ikke og føres i rapporten til forfatteren. 0 funn rettet; ingen runde 2.

Rettet: ingen.

Ført i rapporten (klasse a og h; rettes ikke):

1. (a) RESULTATER.md, grense a: «claude-opus-5-5 solved 59 of 61 (solved share 0.9524)»; 59/61 er 0.9672, mens 0.9524 er snittet av oppgaveskårene (20 av 21 oppgaver med skår 1), slik `loest_andel` i results/p3_registrert.json regnes.
2. (h) data/roykprove/budsjett.md linje 25 oppgir en avlesning av Anthropic-saldoen etter P2.4, og tabellen under er regnet fra den.

Åpne (ikke rettet):

1. (c) NTB-0007 linje 26 «Cost is reported from the API billing.»; metoden bruker `total_cost_usd` slik Claude Code rapporterer det (PREREG.md spørsmål 3). docs/decisions/ endres ikke.
2. (d) data/kvalitet/uavhengig.md linje 9: batchprisen for gpt-6.1-sol (1.00/5.00 USD per million tokens) står uten kilde. data/ endres ikke.
3. (e) PLAN.md linje 21: kartet sier «P4 Freeze of v1.0, with cross-check on amd64 before the freeze if included credit covers it»; krysskontrollen ble ikke kjørt (AVVIK.md nr. 12). Kartet endres ikke.
4. (f) .zenodo.json `"license": "cc-by-4.0"` mot to lisenser i LICENSE, README.md og CITATION.cff (MIT for kode, CC BY 4.0 for dokumenter og data). Feltet tar én lisens-ID, og ingen enkelt ID stemmer med begge; valget er forfatterens.

Etter runden (2026-11-18):

1. Funn (a) er rettet: grense a og innledningen til tabell T4 i RESULTATER.md sier nå at løst andel er snittet av oppgaveskårene, og oppgir kjøringene for seg.
2. Funn (f) er avklart: `.zenodo.json` beholder én lisens-ID (`cc-by-4.0`), og Zenodo-posten føres med begge lisensene (MIT og CC BY 4.0).
