# Sistema degli snapshot

Gli snapshot sono dump PostgreSQL in formato custom pubblicati come asset delle
GitHub Release di
[`xbit18/icvdb-snapshots`](https://github.com/xbit18/icvdb-snapshots).

## Individuazione e convalida

1. Richiede l'URL configurato della latest release.
2. Seleziona il primo asset con nome che termina in `.dump`.
3. Richiede un digest `sha256:` nei metadati dell'asset.
4. Scarica l'asset e verifica SHA256.
5. Esegue `pg_restore --list` prima del ripristino.
6. Ripristina in `icv_db_candidate`, trattando ogni errore come fatale.
7. Si connette al candidato e richiede la presenza di tabelle utente.

Il tag installato viene scritto atomicamente in `/data/state/snapshot-version`
solo dopo sostituzione e convalida finali.

`SNAPSHOT_LATEST_URL` può indicare una risposta compatibile con le release
GitHub. L'implementazione richiede `tag_name`, un asset `.dump`,
`browser_download_url` e un digest GitHub dell'asset.
