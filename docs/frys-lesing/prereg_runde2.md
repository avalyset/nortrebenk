# Frys-lesing runde 2 (prereg), 2026-11-17, HEAD 886c65b (med rettingene fra runde 1 uncommittet)

Ny uavhengig Opus-subagent, filliste pluss prereg_runde1.md. Rettingene 2–9 fra runde 1 står riktig på disk. Retting 1 var feil. 14 funn: 3 rettet (4 endringer), 11 står åpne.

Rettet:

1. (1) Retting 1 fra runde 1 var feil: data/p3_kontroll.jsonl har feltet `tidligere_kjoringer` med de feilede selvtestene for #966 og #2619 og de to ikke-startede forsøkene for kafka-manager #336 (4.9 og 5.9 GiB) → PREREG satt tilbake til «Earlier attempts are recorded in the same file:»; merknad lagt til i prereg_runde1.md.
2. (11) harness/kvalitet/sammenstill.py-docstringen sa at skriptet lager samsvar.md → presisert at samsvar.md ikke skrives av skriptet.
3. (14) tests/test_analyse.py: klassen `VarianterOgMangler` sto etter `if __name__ == "__main__"` og ble ikke kjørt når fila kjøres direkte → blokken flyttet sist.

Åpne (ikke rettet; metode, regler, påstander eller låst kode):

1. data/p3_kontroll.jsonl har et annet radformat enn dagens `kontroll_modus` skriver (felt på toppnivå, `tidligere_kjoringer`), og radene for #330, #1069 og #688 viser selvtesten fra før unntaket for linjer på base. Kontrollen er kjørt med kjøreren fra før rettingen 17.11; PREREG sier ikke dette.
2. NTB-0007 sier at kostnad rapporteres fra API-faktureringen; PREREG og koden bruker `total_cost_usd` fra Claude Code, mens B regnes fra Anthropic-saldoen.
3. «Up to 3 passes of 84 runs» og «the four runs one at a time» stemmer ikke for et pass med bare utvidet tekst (42 kjøringer, to per oppgave).
4. Stopper kjøreren midt i en kjøring (krasj, avbrudd, eller stopp ved nøkkelprefiks i transkriptet), blir det ingen rad; kjøringen tas på nytt, men kostnaden kommer ikke med i brukt eller rapporten.
5. API-feil gjenkjennes på delstrengen «api» i resultatteksten når `is_error` er satt; det slår også til på ord som «rapid» eller «capability».
6. Tidstaket regnes som nådd når veggtiden for hele `docker run` er 2400 s eller mer, også oppstart og diff etter at claude er ferdig.
7. Selvtesten sjekker github.com, registry.npmjs.org og repo.maven.apache.org, ikke NuGet, Gradle-pluginportalen eller Yarn-registret; PREREG sier at pakkeregistre er utilgjengelige og at selvtesten sjekker dette.
8. Kandidatlinjene til selvtesten sorteres etter lengde fra et sett; ved lik lengde avhenger rekkefølgen av PYTHONHASHSEED (gjelder ved grensen for mock-oauth2-server #1069, #1155, #1161 og mellom 3. og 4. linje for pensjonssimulator #688 og access-management-frontend #2625).
9. Cachene fra gulltilstanden for kafka-manager #330 og #336 viser hvilke avhengigheter løsningen bruker og kan inneholde kompilerte byggeskript fra gulltilstanden; NTB-0006 sier at ingen kildeendringer fra gullpatchen følger med, og hintet står ikke blant grensene.
10. vurder.py og samsvar.md: at temperatur ikke kan settes for Claude Sonnet 5.5 (400) har ingen kilde i repoet.
11. PREREG sier «default settings except what sealing requires»; agentbildet setter ti miljøbrytere (blant annet `CLAUDE_CODE_DISABLE_FEATURE_FLAGS`), som ikke er listet i PREREG.
