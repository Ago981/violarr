# Torznab

Violarr espone l'endpoint `/api` per Prowlarr e altri client compatibili.

Operazioni supportate:

- `t=caps`
- `t=search`
- `t=movie`
- `t=tvsearch`

L'endpoint restituisce XML generato con le API per elementi XML di Python:
titoli e valori del database vengono sottoposti a escaping invece di essere
concatenati nel markup.

Consulta il [riferimento delle funzionalità](../reference/torznab-capabilities)
per parametri, categorie, limiti e attributi emessi.
