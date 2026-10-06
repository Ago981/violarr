#!/usr/bin/env bash
set -Eeuo pipefail

: "${PGDATA:=/data/postgres}"
: "${DB_HOST:=127.0.0.1}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=icv_db}"
: "${DB_USER:=icv}"
: "${DB_PASSWORD:=icv_internal}"
: "${SNAPSHOT_STATE_FILE:=/data/state/snapshot-version}"

export PGDATA DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD SNAPSHOT_STATE_FILE

STATE_DIR="$(dirname "$SNAPSHOT_STATE_FILE")"
POSTGRES_PID=""
UVICORN_PID=""

log() {
    echo "[entrypoint] $*"
}

shutdown() {
    trap - SIGTERM SIGINT

    log "Arresto servizi..."

    if [ -n "${UVICORN_PID}" ] && kill -0 "$UVICORN_PID" 2>/dev/null; then
        kill -TERM "$UVICORN_PID" 2>/dev/null || true
        wait "$UVICORN_PID" 2>/dev/null || true
    fi

    if [ -n "${POSTGRES_PID}" ] && kill -0 "$POSTGRES_PID" 2>/dev/null; then
        gosu postgres pg_ctl -D "$PGDATA" -m fast -w stop >/dev/null 2>&1 || true
        wait "$POSTGRES_PID" 2>/dev/null || true
    fi
}

trap shutdown SIGTERM SIGINT

mkdir -p "$PGDATA" "$STATE_DIR"
chown -R postgres:postgres "$PGDATA"
chown -R app:app "$STATE_DIR"

if [ ! -s "$PGDATA/PG_VERSION" ]; then
    log "Prima inizializzazione PostgreSQL..."

    PWFILE="$(mktemp)"
    printf '%s\n' "$DB_PASSWORD" > "$PWFILE"
    chown postgres:postgres "$PWFILE"
    chmod 600 "$PWFILE"

    gosu postgres initdb \
        -D "$PGDATA" \
        --username="$DB_USER" \
        --pwfile="$PWFILE" \
        --encoding=UTF8 \
        --locale=en_US.utf8 \
        --auth-local=trust \
        --auth-host=scram-sha-256

    rm -f "$PWFILE"

    {
        echo
        echo "# icvdb-torznab"
        echo "listen_addresses = '127.0.0.1'"
        echo "port = ${DB_PORT}"
    } >> "$PGDATA/postgresql.conf"
fi

log "Avvio PostgreSQL..."

gosu postgres postgres -D "$PGDATA" &
POSTGRES_PID=$!

for _ in $(seq 1 60); do
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
        break
    fi

    if ! kill -0 "$POSTGRES_PID" 2>/dev/null; then
        log "ERRORE: PostgreSQL si è arrestato durante l'avvio."
        exit 1
    fi

    sleep 1
done

if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
    log "ERRORE: PostgreSQL non è diventato disponibile."
    exit 1
fi

log "PostgreSQL pronto."

if ! PGPASSWORD="$DB_PASSWORD" \
    psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d postgres \
        -Atc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" \
    | grep -qx "1"; then

    log "Creazione database ${DB_NAME}..."

    PGPASSWORD="$DB_PASSWORD" \
    createdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -O "$DB_USER" \
        "$DB_NAME"
fi

if [ ! -s "$SNAPSHOT_STATE_FILE" ]; then
    log "Nessuno snapshot installato. Avvio bootstrap iniziale..."

    gosu app \
        env \
        DB_HOST="$DB_HOST" \
        DB_PORT="$DB_PORT" \
        DB_NAME="$DB_NAME" \
        DB_USER="$DB_USER" \
        DB_PASSWORD="$DB_PASSWORD" \
        DB_AUTO_UPDATE="true" \
        SNAPSHOT_STATE_FILE="$SNAPSHOT_STATE_FILE" \
        python -c \
        "from snapshot_updater import SnapshotUpdater; SnapshotUpdater().update_once()"

    if [ ! -s "$SNAPSHOT_STATE_FILE" ]; then
        log "ERRORE: impossibile installare lo snapshot iniziale."
        exit 1
    fi

    log "Bootstrap completato: $(cat "$SNAPSHOT_STATE_FILE")"
fi

log "Avvio icvdb-torznab..."

gosu app \
    env \
    DB_HOST="$DB_HOST" \
    DB_PORT="$DB_PORT" \
    DB_NAME="$DB_NAME" \
    DB_USER="$DB_USER" \
    DB_PASSWORD="$DB_PASSWORD" \
    DB_UPDATE_START_DELAY="${DB_UPDATE_START_DELAY:-60}" \
    SNAPSHOT_STATE_FILE="$SNAPSHOT_STATE_FILE" \
    uvicorn app:app \
        --host 0.0.0.0 \
        --port 8000 &

UVICORN_PID=$!

set +e
wait -n "$POSTGRES_PID" "$UVICORN_PID"
STATUS=$?
set -e

log "Uno dei servizi si è arrestato (exit code ${STATUS})."
shutdown
exit "$STATUS"