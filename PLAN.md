# PLAN – nortrebenk

**Formål:** måle hvor godt og raskt kodeagenter løser oppgaver fra offentlig kode i norske etater, og hva hver løste oppgave koster. Fasiten er etatens egne tester.

**Brukere:** teknologiledelse i etatene (modellklasse under kostnadstak), DFD/Digdir/DFØ (gevinstmåling uten selvrapportering), forskere på utviklerproduktivitet.

**Start:** P1, lar oppgavene seg kjøre. **Midt:** prereg-v1, alt låst før agentdata. **Ende:** v1.0 med DOI. Kartet slutter der.

## Kart (fast rekkefølge; avvik føres i AVVIK.md)

- P0 Recon og frosset kandidatliste
- P1 Kjøringsvalidering (fail-to-pass)
- P2 Repo, sett og forhåndsregistrering
  - P2.1 Repo og ADR
  - P2.2 Settbygging lokalt på linux/arm64: forsegling, stabilitet over tre kjøringer, tompatch-kontroll, dedup, treningsgrenser
  - P2.3 Kvalitetssjekk av oppgavene
  - P2.3b Utvidet oppgavetekst med krav og grensesnitt, og ny kvalitetssjekk av den (NTB-0013)
  - P2.4 Anker og røykprøve på oppgaver utenfor settet; budsjettak
  - P2.5 Forhåndsregistrering (prereg-v1), med oversettelse av repoets dokumenter til engelsk
- P3 Pilotkjøring under forhåndsregistreringen: Claude Code med Opus 5.5 og med Sonnet 5.5, på utvidet tekst og på PR-teksten alene
- P4 Frys av v1.0, med krysskontroll på amd64 før frys hvis inkludert kreditt dekker det

Status for hver fase står i ground truth, ikke her.

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
- [NTB-0011: Plattform](docs/decisions/NTB-0011-plattform.md)
- [NTB-0012: Budsjettramme](docs/decisions/NTB-0012-budsjettramme.md)
- [NTB-0013: Tekstvarianter](docs/decisions/NTB-0013-tekstvarianter.md)
