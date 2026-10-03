# Safe updates

Snapshot updates avoid restoring over the active database.

## Normal flow

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

Download, checksum, dump, restore, or candidate-validation failures leave the
active database unchanged. A post-switch validation failure attempts to rename
`icv_db_previous` back into service.

Maintenance mode covers only the switch and final validation, not the download
or candidate restore. Requests received in maintenance get a JSON HTTP `503`
response rather than a partial search result.

::: warning Operational boundary Rollback protects the database switch. It is
not a backup strategy for deletion of the `/data` volume. :::
