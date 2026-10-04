# Violarr

[Italiano](README.md) · [English](README.en.md)

**L’integrazione Prowlarr per Il Corsaro Viola.** Violarr è un bridge self-hosted
tra uno snapshot PostgreSQL di ICVDB e client Torznab come Prowlarr. Un solo
container esegue PostgreSQL 16, FastAPI, la WebUI e gli aggiornamenti sicuri del
database.

## Funzionalità

- Ricerche Torznab per film, serie TV e anime
- Configurazione persistente tramite browser
- Ordinamento con preferenza per l'italiano, filtro solo italiano e regole personalizzate limitate
- Configurazione Generic Torznab in Prowlarr derivata dallo schema
- Aggiornamenti degli snapshot tramite database candidato, con verifica SHA256 e rollback
- Un solo volume `/data`; PostgreSQL non è esposto all'host

## Avvio rapido

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

Segui l'avanzamento del primo avvio:

```bash
docker logs -f icvdb-torznab
```

Quando il servizio è pronto, apri la WebUI su `http://localhost:8000/`.
L'endpoint Torznab resta `http://localhost:8000/api`.

Al primo avvio Violarr inizializza PostgreSQL, scarica lo snapshot più recente da
[`xbit18/icvdb-snapshots`](https://github.com/xbit18/icvdb-snapshots), ne verifica
il digest SHA256, lo convalida e lo ripristina, quindi avvia FastAPI.

Per Docker Compose e gli aggiornamenti, consulta la
[documentazione](https://xbit18.github.io/violarr/).

## Elaborazione dei risultati

Il preset predefinito `unfiltered` conserva l'ordinamento di v1.0. I preset
facoltativi possono preferire marcatori italiani espliciti, nascondere i
risultati non italiani o applicare regole strutturate di punteggio ed esclusione.

L'ordinamento modifica solo la risposta ICVDB: non garantisce la selezione da
parte di Radarr o Sonarr. I filtri rigidi rimuovono i risultati prima che
Prowlarr possa riceverli.

## Collegare Prowlarr

1. Apri **Prowlarr** nella WebUI.
2. Inserisci l'URL di Prowlarr e la API key.
3. Imposta come Indexer URL un indirizzo raggiungibile da Prowlarr, per esempio
   `http://icvdb-torznab:8000/api` su una rete Docker condivisa.
4. Salva, verifica la connessione e aggiungi l'indexer.

Non usare `localhost` come Indexer URL se Prowlarr gira in un altro container:
in quel contesto indica il container di Prowlarr stesso.

## Sicurezza

WebUI, WebAPI ed endpoint Torznab non hanno autenticazione. Mantieni la porta
`8000` su una LAN affidabile oppure usa un reverse proxy autenticato. Il
container non richiede un socket Docker e PostgreSQL ascolta solo su
`127.0.0.1:5432` all'interno del container.

## Documentazione

- [Documentazione utente](https://xbit18.github.io/violarr/)
- [Architecture](ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)

## Licenza

MIT
