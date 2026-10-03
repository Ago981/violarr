FROM node:24-bookworm-slim AS frontend-build

WORKDIR /build/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM debian:bookworm-slim

LABEL org.opencontainers.image.source="https://github.com/xbit18/icvdb-torznab"
LABEL org.opencontainers.image.description="Indexer Torznab self-hosted per ICVDB con PostgreSQL e aggiornamenti automatici del database"
LABEL org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:/usr/lib/postgresql/16/bin:$PATH" \
    PGDATA="/data/postgres" \
    DB_HOST="127.0.0.1" \
    DB_PORT="5432" \
    DB_NAME="icv_db" \
    DB_USER="icv" \
    DB_AUTO_UPDATE="true" \
    DB_UPDATE_INTERVAL="86400" \
    DB_UPDATE_START_DELAY="60" \
    SNAPSHOT_STATE_FILE="/data/state/snapshot-version"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
    && install -d /usr/share/postgresql-common/pgdg /etc/postgresql-common \
    && curl --fail --show-error --silent \
        https://www.postgresql.org/media/keys/ACCC4CF8.asc \
        -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
        > /etc/apt/sources.list.d/pgdg.list \
    && echo "create_main_cluster = false" > /etc/postgresql-common/createcluster.conf \
    && printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d \
    && chmod +x /usr/sbin/policy-rc.d \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gosu \
        postgresql-16 \
        postgresql-client-16 \
        python3 \
        python3-venv \
        tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --home-dir /app --shell /usr/sbin/nologin app

WORKDIR /app

COPY requirements.txt .
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY app.py snapshot_updater.py settings.py result_processor.py prowlarr.py webapi.py entrypoint.sh ./
COPY --from=frontend-build /build/frontend/dist /app/frontend-dist

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/tini", "--", "/app/entrypoint.sh"]
