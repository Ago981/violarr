# Integrazione Prowlarr

Configura Prowlarr dalla WebUI invece di creare manualmente un indexer Generic
Torznab.

## Procedura rapida

1. Apri **Prowlarr** nella WebUI.
2. Inserisci l'URL, per esempio `http://prowlarr:9696`.
3. Inserisci una API key Prowlarr.
4. Inserisci l'Indexer URL **raggiungibile da Prowlarr**, per esempio
   `http://icvdb-torznab:8000/api`.
5. Salva, scegli **Verifica connessione**, quindi **Aggiungi indexer**.

::: tip Rete dei container

Nel container Prowlarr, `localhost` indica Prowlarr stesso. Usa il nome del
servizio su una rete Docker condivisa o un altro indirizzo raggiungibile dal
container.

:::

## Funzionamento di Test e Add

**Verifica connessione** interroga `/api/v1/indexer/schema` con l'header
`X-Api-Key`. **Aggiungi indexer** segue lo schema corrente di Prowlarr:

1. seleziona il template Generic Torznab con implementazione `Torznab`;
2. lo clona e imposta il nome visualizzato su `Violarr`;
3. divide l'Indexer URL in `baseUrl` e `apiPath`, lasciando vuoto `apiKey`;
4. confronta gli indexer esistenti per origine e percorso API normalizzati;
5. se non trova corrispondenze, verifica e crea la risorsa.

Le operazioni ripetute sono idempotenti.

## Gestione della API key

- La chiave viene salvata solo se inserita.
- Un campo di sostituzione assente la conserva; un valore vuoto la cancella.
- Le risposte espongono `api_key_configured`, mai la chiave.
- Gli override di runtime non sono copiati nel file delle impostazioni.

## Risposte di errore

`GET /webapi/prowlarr/status` restituisce sempre HTTP `200`; gli errori remoti
appaiono come `connected: false` con un messaggio `error` sanificato. Gli errori
sensibili o inattesi diventano `Prowlarr request failed`. Le route di comando
usano HTTP `502` per errori remoti e HTTP `400` per configurazione mancante.
