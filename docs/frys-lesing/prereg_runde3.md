# Frys-lesing runde 3 (prereg), 2026-11-17, HEAD 886c65b (med rettingene fra runde 1 og 2 uncommittet)

Ny uavhengig Opus-subagent, filliste pluss prereg_runde1.md og prereg_runde2.md. Alle rettingene fra runde 1 og 2 står riktig på disk, og retting 1 fra runde 1 er riktig tilbakeført. 7 nye funn. Dette var siste runde (høyst tre); funnene er ikke rettet og står åpne.

Åpne:

1. Diskporten måles også mellom instansbygget og agentbygget. Er det under 6 GiB der, sletter `rydd_egne()` alle images med label nortrebenk=p2 utenom mellomtjeneren og de vernede, også instansbildet som nettopp ble bygget. Blir det da minst 6 GiB, bygges agentbildet, men kontrollen av vurderingsveien feiler fordi instansbildet mangler, og oppgavens kjøringer blir manglende med grunn «forberedelse feilet», ikke «under 6 GiB ledig». (Metode, låst kode; ikke utløst i data/p3_kontroll.jsonl, laveste verdi 6.5 GiB.)
2. `kjor` og `prove` bruker de samme tilstandsfilene i NTB_UT (standard ./ntb-ut). Startes `kjor` i generalprøvens NTB_UT, blir generalprøvens B, kostnad og pass 1 regnet som P3. Ingen sperre i koden, og verken PREREG eller harness/agent/BRUK.md sier at modusene skal ha hver sin NTB_UT. (Metode, låst kode.)
3. PREREG l. 5 sier at beslutningsverdiene er kodet i harness/agent/kjor_p3.py; tidstaket på 40 minutter er i kjor_agent.py (l. 86 nevner begge). (Redaksjonelt.)
4. README sier at feltnavnene i datafilene forklares i ordlista; mange norske feltnavn mangler (f.eks. `utelukket`, `valgt_regel`, `bestatt`, `steg`, `tidligere_kjoringer`, `aarsak`, `tester_gaar_uten_nett`, `kjoreklasse`, `treningsgrense`). (Redaksjonelt.)
5. data/kandidater_v1.jsonl (194 rader) er ikke omtalt i noe dokument; regelen som ga de 30 P1-kandidatene (klasse A og lisens MIT) står ikke beskrevet. (Redaksjonelt.)
6. PLAN.md l. 27: lenketeksten «Scope, benefit and limits» mot tittelen «Scope, utility and limits» i NTB-0001. (Skrivefeil.)
7. PLAN.md: kartet har steget P2.3b fra AVVIK nr. 7, men ikke generalprøven fra AVVIK nr. 8. (Redaksjonelt.)
