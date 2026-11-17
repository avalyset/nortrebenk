# Frys-lesing runde 1 (prereg), 2026-11-17, HEAD 886c65b (med PREREG.md og README.md fra punkt 5 uncommittet)

Uavhengig Opus-subagent, kun filliste. 34 funn. Etter regelen for frysen rettes foreldet status, feil tall mot disk, brutte stier og skrivefeil; funn om metode, design, regler eller hva studien påstår rettes ikke, og koden i harness/agent endres ikke etter generalprøven. 8 funn rettet (9 endringer), 26 står åpne.

Rettet:

1. (18) PREREG sa at tidligere kontrollforsøk står i data/p3_kontroll.jsonl; fila har bare de seks beståtte → «Earlier attempts are not in that file; they are recorded in the author's internal repository:». REVERSERT i runde 2: funnet var feil; fila har feltet `tidligere_kjoringer` med forsøkene (se prereg_runde2.md).
2. (34) PREREG «1 turns» → «1 turn».
3. (34) NTB-0007 «If the budget cap is not reached, runs are cut» (snudd betingelse i oversettelsen) → «If the budget cap does not suffice, runs are cut».
4. (6) PREREG nevnte ikke endringslinjene i NTB-0003/0004/0007/0008/0011 fra commit 8ebc9b3 (etter P2.3-utfallet i 7933a07) → lagt til i setningen om endringer etter P2.3.
5. (21) NTB-0014 «P3 takes three passes» → «up to three passes».
6. (22) NTB-0014 «measured at most 9.43 USD for one round» → «gave at most 9.43 USD …, computed from the highest cost measured per arm on two tasks outside the set».
7. (24) NTB-0002 «README describes the runner» → «harness/BRUK.md describes the runner».
8. (19) harness/agent/BRUK.md beskrev selvtesten som «the gold patch's three longest added lines» → opptil tre, minst 30 tegn, høyst ti kandidater, linjer på base hoppes over.
9. (27) harness/scripts/p22_kjor.py docstring «p2/msb_repos» → «harness/msb_repos».

Åpne (ikke rettet; metode, regler, påstander eller låst kode):

1. `kodesprak` er repospråk, ikke språket i oppgavens patch (altinn-support-dashboard #970 er C#, kafka-manager #329/#330/#337 mest TypeScript); PREREG, README, NTB-0004 og samsvar.md sier «Kotlin and TypeScript».
2. Andre unntak fra kjor_agent.kjør() (f.eks. tidsavbrudd i vurder() etter at agenten har kjørt) blir forkastede forsøk med kostnad 0 i kjor_p3; kostnaden kommer ikke med i brukt eller i rapporten, og slike unntak er ikke nevnt i definisjonen av infrastrukturfeil.
3. Claude Code kan gå over budsjettaket (generalprøven: tak 0.02, kostnad 0.0441); budsjettregelen og kostnadsregelen ved tidstak forutsetter at taket holder.
4. Takene i generalprøven ble provosert med et skript i det interne repoet (TIDSGRENSE satt til 25 s, budsjett 0.02); repoet har ingen kode som skriver feltet `taktest` eller rader med `pass` null.
5. NTB-0006 sier at avhengigheter for gulltilstanden løses i bildet; det gjelder bare de to oppgavene med `bygg`.
6. NTB-0007 (tre kjøringer per arm og oppgave; tak per oppgave) er ikke merket som endret av NTB-0014 (inntil tre pass, tak per kjøring).
7. NTB-0008 sier kostnad «including failed ones»; PREREG og analyse.py tar bare gjennomførte kjøringer.
8. analyse.py-docstringen sier at avviket mellom likning (4) og vedlegg A er «ført som åpent punkt»; punktet finnes ikke i repoet.
9. Uten `--pass` regner analyse.py alle pass som fullførte; kallet er ikke låst i PREREG.
10. AVVIK nr. 5 sier uten forbehold at kjøreren kontrolleres mot Multi-SWE-bench i P4; NTB-0011 og PREREG gjør det betinget av kreditt.
11. Forankringene og OTS-bevisene oppgis med kilde i forfatterens interne repo og er ikke med i depositumet.
12. Står alle ti kandidatlinjer i base-commiten, feiler selvtesten og oppgavens kjøringer blir manglende; PREREG nevner ikke følgen. (Den statiske selvtestsjekken 17.11 ga tre sjekkede linjer for alle 21 oppgavene.)
13. Mellomtjenerens avvisning av nettverktøy slipper forespørselen videre hvis kroppen ikke kan dekodes.
14. Sperren sjekker bare at PREREG_DOI.txt finnes; `kjor_agent.py kjor` har ingen sperre.
15. Diskporten måler `NTB_DISK` (standard `/`); hvilken disk som måles, er ikke låst i PREREG.
16. NTB-0013 sier at tilleggene ikke nevner testene; det er ikke en mekanisk kontroll, og utvidet tekst for kafka-manager #336 nevner testavhengigheter.
17. NTB-0006 «without remotes and without refs» mot «one ref» i harness/BRUK.md, PREREG og _felles.py; NTB-0006 tilskriver bortfallet av registersetningen NTB-0011.
18. NTB-0001 viser til relatert arbeid i README og et datablad som ikke finnes.
19. README og PREREG sier «preregistered»/«frozen at git tag prereg-v1» før taggen og DOI-en finnes (ventet før frysen).
20. PLAN.md viser til status i ground truth, som ikke er i repoet.
21. Docstringer i harness/agent med foreldede stier: budsjett.py («c6_budsjett.py»), gullcache.py («p24/scripts/b4_nett.py»).
22. Skriptene som lager uavhengig_utvidet.jsonl/uavhengig.md, generalprove.jsonl, p24_nett.jsonl, anker/msb_altinn.jsonl og dedup.md er ikke i repoet.
23. Eksterne tall uten kilde: batchpris i uavhengig.md, PRISER og «15 kall per minutt» i vurder.py, JOSS-sjekklisten i NTB-0009.
24. Lisens: README «data under CC BY 4.0» mot LICENSE (tredjepartsdata beholder kildelisensen); LICENSE nevner ikke tests/ og nevner Apache-2.0; .zenodo.json og CITATION.cff har ulike lisenslister.
25. .zenodo.json og CITATION.cff beskriver programvare uten versjon, ikke forhåndsregistreringen.
26. README-ordlista gir `status` bare verdiene for kjøringsfilene; andre datafiler bruker andre verdier.
