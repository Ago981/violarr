# WebUI

Apri `http://HOST:8000/` per controllare il servizio e gestire le impostazioni
supportate. La WebUI è un'applicazione Vue same-origin servita da FastAPI nello
stesso container.

## Sezioni disponibili

| Sezione                | Scopo                                                       |
| ---------------------- | ----------------------------------------------------------- |
| Dashboard              | Stato di database, updater, risultati e cache Prowlarr      |
| Aggiornamenti database | Abilitazione e intervallo degli aggiornamenti               |
| Elaborazione risultati | Selezione del preset e modifica delle regole personalizzate |
| Prowlarr               | Connessione, verifica dell'accesso e aggiunta dell'indexer  |

Le modifiche sono salvate in `/data/state/settings.json`. La UI non rilegge mai
una API key Prowlarr salvata: riceve solo `api_key_configured`.

::: tip Valori controllati dall'ambiente

Le variabili d'ambiente hanno priorità sulle impostazioni persistenti. Un valore
di runtime può risultare attivo nella UI senza essere scritto in
`settings.json`.

:::

## Esposizione di rete

La WebUI e il backend `/webapi` non hanno autenticazione. Esponili solo su una
rete affidabile o dietro un reverse proxy autenticato.
