# Collegare Prowlarr

Collega Prowlarr dalla WebUI e aggiungi Violarr come indexer.

## Procedura rapida

1. In Prowlarr copia la chiave da **Settings → General → Security → API Key**.
2. Apri **Prowlarr** nella WebUI di Violarr.
3. Inserisci **URL Prowlarr**, per esempio `http://prowlarr:9696`.
4. Inserisci la **Chiave API**.
5. Inserisci l'**URL indexer visto da Prowlarr**, per esempio
   `http://icvdb-torznab:8000/api`.
6. Premi **Salva impostazioni Prowlarr**, quindi **Verifica connessione**.
7. Quando lo stato è **Connesso**, premi **Aggiungi Violarr a Prowlarr**.

::: tip Rete dei container

Nel container Prowlarr, `localhost` indica Prowlarr stesso. Usa il nome del
servizio su una rete Docker condivisa o un altro indirizzo raggiungibile dal
container.

:::

## Risultato atteso

- La WebUI mostra **Connesso**.
- Prowlarr contiene un indexer chiamato **Violarr**.
- Ripetere l'aggiunta non crea duplicati.

## Modificare la chiave

- Una chiave già salvata resta attiva finché non scegli **Sostituisci chiave** o
  **Cancella la chiave API salvata** e salvi.
- Se il test fallisce, controlla URL, chiave e rete dei container nella
  [risoluzione dei problemi](../troubleshooting).
