# Variabili d'ambiente

Violarr carica la configurazione in questo ordine:

1. valori predefiniti;
2. impostazioni persistenti salvate dalla WebUI;
3. eventuali override espliciti tramite variabili d'ambiente.

Le variabili d'ambiente hanno quindi priorità sulle impostazioni salvate, ma
vengono considerate override solo quando sono effettivamente definite
dall'utente.

## Override per l'utente

| Variabile                | Default applicativo            | Effetto                                                             |
| ------------------------ | ------------------------------ | ------------------------------------------------------------------- |
| `DB_AUTO_UPDATE`         | `true`                         | Override dello stato degli aggiornamenti automatici                 |
| `DB_UPDATE_INTERVAL`     | `86400`                        | Override dell'intervallo in secondi; valori validi 60–604800        |
| `DB_UPDATE_START_DELAY`  | `60`                           | Ritardo prima del primo controllo periodico                         |
| `ICVDB_RESULT_PRESET`    | `unfiltered`                   | Override del preset attivo                                          |
| `ICVDB_PROWLARR_URL`     | vuoto                          | Override dell'URL base di Prowlarr                                  |
| `ICVDB_PROWLARR_API_KEY` | vuoto                          | Override della API key di Prowlarr                                  |
| `PROWLARR_API_KEY`       | vuoto                          | Override compatibile; prevale se sono impostate entrambe le API key |
| `PROWLARR_INDEXER_URL`   | vuoto                          | Override dell'URL Torznab fornito a Prowlarr                        |
| `SNAPSHOT_LATEST_URL`    | GitHub latest-release API      | Cambia la sorgente dei metadati degli snapshot                      |
| `SNAPSHOT_STATE_FILE`    | `/data/state/snapshot-version` | Cambia il percorso dello stato della versione installata            |
| `ICVDB_SETTINGS_PATH`    | `/data/state/settings.json`    | Cambia il percorso delle impostazioni                               |

`DB_AUTO_UPDATE` e `DB_UPDATE_INTERVAL` normalmente non devono essere
specificati nel container. In questo modo i valori configurati dalla WebUI
vengono salvati in `/data/state/settings.json` e applicati immediatamente
all'updater.

Se una di queste variabili viene specificata esplicitamente, il suo valore
diventa invece un override runtime e prevale sulla configurazione salvata.

Per esempio:

```yaml
environment:
  DB_UPDATE_INTERVAL: '3600'
```

forza un intervallo di un'ora anche se dalla WebUI viene configurato un valore
diverso.

## Variabili interne di runtime

L'immagine fornisce questi valori per PostgreSQL incorporato. Una normale
installazione a container singolo non dovrebbe modificarli.

| Variabile           | Valore dell'immagine            |
| ------------------- | ------------------------------- |
| `DB_HOST`           | `127.0.0.1`                     |
| `DB_PORT`           | `5432`                          |
| `DB_NAME`           | `icv_db`                        |
| `DB_USER`           | `icv`                           |
| `DB_PASSWORD`       | valore interno al container     |
| `DB_ADMIN_DB`       | `postgres` se non impostato     |
| `FRONTEND_DIST_DIR` | `/app/frontend-dist` se assente |

::: warning Segreti

Usa secret del container o configurazioni protette per le API key.
L'applicazione maschera le chiavi nelle risposte, ma non cifra i valori salvati
in `settings.json`.

:::
