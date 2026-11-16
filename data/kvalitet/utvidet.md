# Kvalitetssjekk av utvidet oppgavetekst (P2.3b)

Hver oppgave er vurdert på nytt med den utvidede teksten (PR-teksten med krav og grensesnitt, `data/utvidet_tekst.jsonl`) i stedet for PR-teksten, med samme prompt, samme vurderere og samme regel («minst 2 av 3») som i P2.3 (NTB-0004, NTB-0013). OpenAI-vurdereren er bare kalt der nøyaktig én av de to andre stemte for utelukkelse på et kriterium.

## Utfall

- består: 21
- utelukket: 0
- uavklart: 0
- tillegg_feilet: 0

## Per oppgave

Skårene er underspecified/false_negative. A = claude-sonnet-5-5, O = gpt-6.1-sol, G = gemini-3.5-flash-lite; «–» = ikke kalt.

| Oppgave | A P2.3 | O P2.3 | G P2.3 | Utfall P2.3 | A nå | O nå | G nå | Utfall nå |
|---|---|---|---|---|---|---|---|---|
| navikt/mock-oauth2-server #1069 | 1/0 | 0/0 | 0/0 | består | 1/1 | – | 0/0 | består |
| navikt/mock-oauth2-server #1131 | 1/1 | 0/0 | 0/0 | består | 1/1 | – | 0/0 | består |
| navikt/mock-oauth2-server #1154 | 1/1 | 0/0 | 0/0 | består | 1/1 | – | 0/0 | består |
| navikt/mock-oauth2-server #1155 | 2/3 | 0/2 | 0/0 | utelukket | 0/0 | – | 0/0 | består |
| navikt/mock-oauth2-server #1161 | 1/2 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/pensjonssimulator #688 | 2/2 | 1/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/pensjonssimulator #692 | 3/3 | 1/2 | 1/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/pensjonssimulator #702 | 3/3 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/pensjonssimulator #715 | 2/2 | 1/2 | 1/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/kafka-manager #329 | 3/3 | 0/2 | 0/0 | utelukket | 0/0 | – | 0/0 | består |
| navikt/kafka-manager #330 | 3/3 | 0/3 | 1/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/kafka-manager #336 | 3/3 | 1/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| navikt/kafka-manager #337 | 2/2 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-support-dashboard #966 | 2/2 | 0/2 | 0/0 | utelukket | 0/1 | – | 0/0 | består |
| Altinn/altinn-support-dashboard #970 | 1/1 | 0/0 | 0/0 | består | 0/0 | – | 0/0 | består |
| Altinn/altinn-support-dashboard #979 | 3/3 | 2/2 | 3/0 | utelukket | 1/0 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2619 | 3/3 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2625 | 2/2 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2642 | 2/3 | 1/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2644 | 3/3 | 0/2 | 0/0 | utelukket | 1/1 | – | 0/0 | består |
| Altinn/altinn-access-management-frontend #2645 | 1/2 | 0/2 | 0/0 | utelukket | 0/1 | – | 0/0 | består |

## OpenAI-vurdereren kalt for

- ingen

## Grenser (NTB-0013)

- Endringen er gjort etter at utfallet av P2.3 og røykprøven var kjent, og før noen agentkjøring på oppgavene i settet. Den er tidsstemplet før tilleggene ble laget.
- Tilleggene er skrevet av en modell fra samme leverandør som agentene (claude-opus-5-5), uten menneskelig kontroll.
- At en oppgave består, kan hvile på vurdereren fra samme leverandør som agentene.
- Tilleggene oppgir navn og strenger fra løsningen.
- Ingen oppgave er fjernet fra `instances.jsonl`; settet fryses i P2.5.
