# Changelog

## Non rilasciato — v1.1.0

Il lavoro in corso per v1.1.0 aggiunge:

- impostazioni WebUI persistenti con schema v1 e segreti Prowlarr mascherati;
- preset deterministici e regole personalizzate per elaborare i risultati;
- endpoint same-origin `/webapi` e installazione Prowlarr derivata dallo schema;
- una WebUI Vue servita dallo stesso container di runtime;
- questo sito di documentazione bilingue basato su Markdown.

L'immagine della release non è stata pubblicata e la verifica Docker non è
completa. Per i dettagli di compatibilità e la cronologia ufficiale consulta
[`CHANGELOG.md`](https://github.com/xbit18/violarr/blob/main/CHANGELOG.md).

## Comportamento v1.0 mantenuto

Il contratto Torznab `/api`, PostgreSQL 16, la porta `8000`, il singolo volume
`/data`, la sorgente degli snapshot e la sicurezza degli aggiornamenti tramite
database candidato restano la base di compatibilità.
