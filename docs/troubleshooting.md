# Risoluzione dei problemi

Inizia dai log del container:

```bash
docker logs -f icvdb-torznab
```

## La WebUI non si apre

- Verifica che la porta `8000` sia pubblicata.
- Esegui `curl 'http://localhost:8000/api?t=caps'`.
- Verifica che il container usi `ghcr.io/xbit18/violarr:latest` e ricrealo dopo
  aver scaricato l'immagine aggiornata.
- Un checkout dei sorgenti deve compilare gli asset frontend prima che FastAPI
  possa servirli.

## Il primo avvio richiede molto tempo

Una nuova installazione scarica, verifica, ispeziona e ripristina un dump
PostgreSQL prima di avviare FastAPI. Segui i log e conserva il volume `/data`.

## Il test di Prowlarr fallisce

1. Verifica che l'URL di Prowlarr sia raggiungibile dal container Violarr.
2. Verifica la API key in **Settings → General** di Prowlarr.
3. Tra container non usare `localhost`, salvo una condivisione del namespace di
   rete.
4. Verifica che Prowlarr esponga lo schema Generic Torznab.

## L'aggiunta riesce ma le ricerche falliscono

L'Indexer URL deve terminare con `/api` ed essere raggiungibile dal **container
Prowlarr**. Provalo dalla rete corretta, non solo dal browser sull'host.

## Mancano risultati attesi

- `italian_only` e le regole di esclusione sono filtri rigidi.
- L'ordinamento è locale a finestre di 1000 righe.
- L'elaborazione non garantisce la selezione di Radarr o Sonarr.
- Torna a `unfiltered` per confrontare l'ordine originale.

## L'aggiornamento è temporaneamente indisponibile

HTTP `503` con `Retry-After: 5` è previsto durante la breve sostituzione del
database. Gli errori persistenti compaiono nella dashboard e nei log. Prima
della sostituzione, un errore lascia invariato il database attivo.

## Le impostazioni non corrispondono al file salvato

Controlla le [variabili d'ambiente](./configuration/environment): gli override
di runtime prevalgono sui valori persistenti senza riscrivere `settings.json`.
