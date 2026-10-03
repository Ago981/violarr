FROM postgres:16-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PGDATA="/data/postgres" \
    DB_HOST="127.0.0.1" \
    DB_PORT="5432" \
    DB_NAME="icv_db" \
    DB_USER="icv" \
    DB_PASSWORD="icv_internal" \
    DB_AUTO_UPDATE="true" \
    DB_UPDATE_INTERVAL="86400" \
    DB_UPDATE_START_DELAY="60" \
    SNAPSHOT_STATE_FILE="/data/state/snapshot-version"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
        ca-certificates \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --home-dir /app --shell /usr/sbin/nologin app

WORKDIR /app

COPY requirements.txt .
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY app.py snapshot_updater.py entrypoint.sh ./

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/tini", "--", "/app/entrypoint.sh"]
