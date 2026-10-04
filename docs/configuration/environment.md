# Variabili d'ambiente

La priorità è: valori predefiniti, impostazioni persistenti, override di
runtime. Gli override sono efficaci senza riscrivere
`/data/state/settings.json`.

## Override per l'utente

| Variabile                | Valore predefinito             | Effetto                                                               |
| ------------------------ | ------------------------------ | --------------------------------------------------------------------- |
| `DB_AUTO_UPDATE`         | `true`                         | Sostituisce lo stato degli aggiornamenti automatici                   |
| `DB_UPDATE_INTERVAL`     | `86400`                        | Intervallo in secondi; valori validi 60–604800                        |
| `DB_UPDATE_START_DELAY`  | `60`                           | Ritardo prima del primo controllo periodico                           |
| `ICVDB_RESULT_PRESET`    | `unfiltered`                   | Sostituisce il preset attivo                                          |
| `ICVDB_PROWLARR_URL`     | vuoto                          | Sostituisce l'URL base di Prowlarr                                    |
| `ICVDB_PROWLARR_API_KEY` | vuoto                          | Sostituisce la API key di Prowlarr                                    |
| `PROWLARR_API_KEY`       | vuoto                          | Override compatibile; prevale se sono impostate entrambe le variabili |
| `PROWLARR_INDEXER_URL`   | vuoto                          | Sostituisce l'URL Torznab fornito a Prowlarr                          |
| `SNAPSHOT_LATEST_URL`    | GitHub latest-release API      | Cambia la sorgente dei metadati degli snapshot                        |
| `SNAPSHOT_STATE_FILE`    | `/data/state/snapshot-version` | Cambia il percorso dello stato della versione installata              |
| `ICVDB_SETTINGS_PATH`    | `/data/state/settings.json`    | Cambia il percorso delle impostazioni                                 |

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
