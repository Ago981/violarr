# Schema di configurazione

Lo schema impostazioni versione 1 è salvato atomicamente in
`/data/state/settings.json`.

## Struttura

```json
{
  "schema_version": 1,
  "database_update": {
    "enabled": true,
    "interval_seconds": 86400
  },
  "result_processing": {
    "preset": "unfiltered",
    "custom_rules": []
  },
  "prowlarr": {
    "url": "",
    "indexer_url": "",
    "api_key": ""
  }
}
```

Le risposte di lettura sostituiscono `api_key` con il booleano
`api_key_configured`.

## Priorità

```text
built-in defaults < persisted settings < runtime environment overrides
```

Il salvataggio dalla WebUI parte dai valori persistenti, evitando di copiare su
disco gli override effettivi dell'ambiente.

## Convalida

- Il documento contiene esattamente i quattro campi principali mostrati.
- `schema_version` è il numero `1`.
- L'intervallo è un intero tra 60 e 604800 secondi.
- Il preset è `unfiltered`, `italian_preferred`, `italian_only` o `custom`.
- Gli URL Prowlarr sono vuoti oppure URL HTTP(S) assoluti senza credenziali.
- Le API key sono stringhe lunghe al massimo 4096 caratteri.
- Le regole seguono il [contratto limitato](../features/custom-filters).

## Aggiornamento dei segreti

Per `PUT /webapi/settings`: ometti `api_key` per conservarla, invia una stringa
non vuota per sostituirla o una stringa vuota per cancellarla. Una chiave
fornita dall'ambiente può restare attiva perché gli override hanno priorità
superiore.
