# Installazione

Avvia Violarr e raggiungi la WebUI con un solo comando.

Servono Docker e una connessione Internet per il primo avvio.

## Procedura rapida

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

Il primo avvio può richiedere alcuni minuti. Segui lo stato con
`docker logs -f icvdb-torznab`.

Quando il servizio è pronto:

- i log indicano che il servizio è pronto;
- la WebUI si apre su `http://localhost:8000/`;
- la dashboard mostra il database come connesso.

## Passo successivo

Continua con la [prima configurazione](./first-setup).
