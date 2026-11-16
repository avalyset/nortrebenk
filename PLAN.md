# PLAN – nortrebenk

Formål, brukere, start/midt/ende og kart er hentet ordrett fra den håndførte delen av ground truth (16.11.2026).

**Formål:** måle hvor godt og raskt kodeagenter løser oppgaver fra offentlig kode i norske etater, og hva hver løste oppgave koster. Fasiten er etatens egne tester.

**Brukere:** teknologiledelse i etatene (modellklasse under kostnadstak), DFD/Digdir/DFØ (gevinstmåling uten selvrapportering), forskere på utviklerproduktivitet.

**Start:** P1, lar oppgavene seg kjøre. **Midt:** prereg-v1, alt låst før agentdata. **Ende:** v1.0 med DOI. Kartet slutter der.

**Kart (fast rekkefølge, avvik bare i AVVIK.md):**
- P0 Recon og frosset kandidatliste: ferdig 16.11.2026 (norpref 1e69c51)
- P1 Kjøringsvalidering: ferdig 16.11.2026, terskel nådd (nortrebenk-intern 84f6d46). Tallene står i del 3.
- P2.1 Repo ~/dev/nortrebenk og ADR NTB-0001–0010
- P2.2 Settbygging: amd64-prøve på Modal (ett repo først), stabilitet 3/3, dedup, treningsgrenser, forsegling, gull- og tompatch-kontroll
- P2.3 Kvalitetssjekk av oppgavene
- P2.4 Anker og røykprøve på oppgaver utenfor settet; budsjettak
- P2.5 Prereg. Port: Eirik godkjenner frys av prereg-v1
- P3 Pilotkjøring under prereg; Claude-armene først
- P4 Frys v1.0. Port: Eirik godkjenner Zenodo og offentlig push

## Beslutninger (ADR)

- [NTB-0001: Omfang, nytte og grenser](docs/decisions/NTB-0001-omfang-nytte-grenser.md)
- [NTB-0002: Format, plattform og kjører](docs/decisions/NTB-0002-format-plattform-kjorer.md)
- [NTB-0003: Inklusjon i settet](docs/decisions/NTB-0003-inklusjon.md)
- [NTB-0004: Kvalitetssjekk](docs/decisions/NTB-0004-kvalitetssjekk.md)
- [NTB-0005: Agentspor](docs/decisions/NTB-0005-agentspor.md)
- [NTB-0006: Forsegling](docs/decisions/NTB-0006-forsegling.md)
- [NTB-0007: Agenter, modeller og betaling](docs/decisions/NTB-0007-agenter-modeller-betaling.md)
- [NTB-0008: Metrikker og analyse](docs/decisions/NTB-0008-metrikker-analyse.md)
- [NTB-0009: Publisering, vedlikehold og pensjonering](docs/decisions/NTB-0009-publisering-vedlikehold-pensjonering.md)
- [NTB-0010: Personopplysninger](docs/decisions/NTB-0010-personopplysninger.md)
