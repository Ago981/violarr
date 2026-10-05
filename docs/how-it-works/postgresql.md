# PostgreSQL

PostgreSQL 16 gira nel container applicativo. Ascolta su `127.0.0.1:5432`, viene
usato da FastAPI e dall'updater e non è pubblicato sull'host.

I dati persistenti risiedono in `/data/postgres`. Il servizio considera lo
schema ICVDB un modello esterno e usa query di sola lettura durante le normali
richieste. I valori HTTP passano attraverso il parameter binding di psycopg.

## Ruoli dei database durante gli aggiornamenti

| Nome               | Scopo                                  |
| ------------------ | -------------------------------------- |
| `icv_db`           | Database applicativo attivo            |
| `icv_db_candidate` | Destinazione di ripristino e convalida |
| `icv_db_previous`  | Sorgente temporanea per il rollback    |

Non esporre la porta `5432` e non montare un secondo volume per il database. Il
confine di persistenza supportato è il singolo volume `/data`.
