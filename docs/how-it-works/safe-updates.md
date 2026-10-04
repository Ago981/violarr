# Aggiornamenti sicuri

Gli aggiornamenti non ripristinano lo snapshot sul database attivo.

## Flusso normale

```text
download and verify
        ↓
restore icv_db_candidate
        ↓
validate candidate
        ↓
enable maintenance (HTTP 503, Retry-After: 5)
        ↓
icv_db → icv_db_previous
icv_db_candidate → icv_db
        ↓
validate active database
        ↓
write snapshot-version and remove previous database
```

Errori di download, checksum, dump, ripristino o convalida del candidato
lasciano invariato il database attivo. Se fallisce la convalida successiva alla
sostituzione, il sistema prova a ripristinare `icv_db_previous`.

La manutenzione copre solo sostituzione e convalida finale, non download o
ripristino. Le richieste ricevute in questa fase ottengono una risposta JSON
HTTP `503`, non risultati parziali.

::: warning Confine operativo

Il rollback protegge la sostituzione del database, ma non sostituisce un backup
contro l'eliminazione del volume `/data`.

:::
