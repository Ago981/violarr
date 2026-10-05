# Changelog

## v1.1.2 - 2026-10-05
### Aggiunte
- supporto per immagini arm64
  
## v1.1.1 — 2026-10-05

v1.1.1 risolve:
 - payload limiter troppo piccolo per Prowlarr
 - bug nel flow per aggiungere Violarr a Prowlarr

Per i dettagli di compatibilità e la cronologia completa consulta
[`CHANGELOG.md`](https://github.com/xbit18/violarr/blob/main/CHANGELOG.md).

## v1.1.0 — 2026-10-05

v1.1.0 aggiunge:

- impostazioni WebUI persistenti con schema v1 e segreti Prowlarr mascherati;
- preset deterministici e regole personalizzate per elaborare i risultati;
- endpoint same-origin `/webapi` e installazione Prowlarr derivata dallo schema;
- una WebUI Vue servita dallo stesso container di runtime;
- questo sito di documentazione bilingue basato su Markdown.

## Comportamento v1.0 mantenuto

Il contratto Torznab `/api`, PostgreSQL 16, la porta `8000`, il singolo volume
`/data`, la sorgente degli snapshot e la sicurezza degli aggiornamenti tramite
database candidato restano la base di compatibilità.
