import asyncio
import hashlib
import json
import os
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

import psycopg
from fastapi import FastAPI, Request as FastAPIRequest
from fastapi.responses import JSONResponse
from psycopg import sql


LATEST_RELEASE_URL = os.getenv(
    "SNAPSHOT_LATEST_URL",
    "https://api.github.com/repos/xbit18/icvdb-snapshots/releases/latest",
)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _tag_date(tag: str) -> date | None:
    if not tag.startswith("db-"):
        return None

    try:
        return date.fromisoformat(tag[3:])
    except ValueError:
        return None


@dataclass(frozen=True)
class Snapshot:
    version: str
    name: str
    url: str
    digest: str


class SnapshotUpdater:
    def __init__(self) -> None:
        self.enabled = _env_bool("DB_AUTO_UPDATE", True)
        self.interval = int(os.getenv("DB_UPDATE_INTERVAL", "86400"))
        self.start_delay = int(os.getenv("DB_UPDATE_START_DELAY", "5"))

        self.db_host = os.getenv("DB_HOST", "db")
        self.db_port = int(os.getenv("DB_PORT", "5432"))
        self.db_name = os.getenv("DB_NAME", "icv_db")
        self.db_user = os.getenv("DB_USER", "icv")
        self.db_password = os.getenv("DB_PASSWORD", "")
        self.admin_db = os.getenv("DB_ADMIN_DB", "postgres")

        self.state_file = Path(
            os.getenv("SNAPSHOT_STATE_FILE", "/data/snapshot-version")
        )

        self.maintenance = threading.Event()
        self._update_lock = threading.Lock()
        self._task: asyncio.Task | None = None

    def _log(self, message: str) -> None:
        print(f"[snapshot-updater] {message}", flush=True)

    def _connection_kwargs(self, dbname: str) -> dict:
        return {
            "host": self.db_host,
            "port": self.db_port,
            "dbname": dbname,
            "user": self.db_user,
            "password": self.db_password,
            "connect_timeout": 10,
        }

    # ------------------------------------------------------------------
    # GitHub release
    # ------------------------------------------------------------------

    def get_latest_snapshot(self) -> Snapshot:
        request = Request(
            LATEST_RELEASE_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "icvdb-torznab",
            },
        )

        with urlopen(request, timeout=30) as response:
            release = json.load(response)

        dump_assets = [
            asset
            for asset in release.get("assets", [])
            if asset.get("name", "").endswith(".dump")
        ]

        if not dump_assets:
            raise RuntimeError(
                "La latest release non contiene alcun asset .dump"
            )

        asset = dump_assets[0]
        digest = asset.get("digest")

        if not digest or not digest.startswith("sha256:"):
            raise RuntimeError(
                "L'asset dello snapshot non espone un digest SHA256 valido"
            )

        return Snapshot(
            version=release["tag_name"],
            name=asset["name"],
            url=asset["browser_download_url"],
            digest=digest,
        )

    # ------------------------------------------------------------------
    # Stato locale
    # ------------------------------------------------------------------

    def read_local_version(self) -> str | None:
        try:
            version = self.state_file.read_text(encoding="utf-8").strip()
            return version or None
        except FileNotFoundError:
            return None

    def write_local_version(self, version: str) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        temporary = self.state_file.with_suffix(".tmp")
        temporary.write_text(f"{version}\n", encoding="utf-8")

        os.replace(temporary, self.state_file)

    def _needs_update(self, local: str | None, remote: str) -> bool:
        if local is None:
            return True

        if local == remote:
            return False

        local_date = _tag_date(local)
        remote_date = _tag_date(remote)

        if local_date is not None and remote_date is not None:
            return remote_date > local_date

        # Se i tag non rispettano il formato atteso, per sicurezza
        # consideriamo diversa la release e proviamo ad aggiornarla.
        return True

    # ------------------------------------------------------------------
    # Download e verifica
    # ------------------------------------------------------------------

    def download_snapshot(self, snapshot: Snapshot) -> Path:
        fd, raw_path = tempfile.mkstemp(
            prefix="icvdb-",
            suffix=".dump",
        )
        os.close(fd)

        path = Path(raw_path)
        hasher = hashlib.sha256()

        request = Request(
            snapshot.url,
            headers={"User-Agent": "icvdb-torznab"},
        )

        try:
            self._log(f"Download di {snapshot.name}...")

            with urlopen(request, timeout=60) as response, path.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break

                    output.write(chunk)
                    hasher.update(chunk)

            actual_digest = f"sha256:{hasher.hexdigest()}"

            if actual_digest != snapshot.digest:
                raise RuntimeError(
                    "Checksum SHA256 non valido: "
                    f"atteso {snapshot.digest}, ottenuto {actual_digest}"
                )

            self._log("SHA256 verificato.")

            subprocess.run(
                ["pg_restore", "--list", str(path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )

            self._log("Dump PostgreSQL valido.")

            return path

        except Exception:
            path.unlink(missing_ok=True)
            raise

    # ------------------------------------------------------------------
    # PostgreSQL helpers
    # ------------------------------------------------------------------

    def _admin_connection(self):
        return psycopg.connect(
            **self._connection_kwargs(self.admin_db),
            autocommit=True,
        )

    def _database_exists(self, connection, name: str) -> bool:
        row = connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (name,),
        ).fetchone()

        return row is not None

    def _terminate_connections(self, connection, name: str) -> None:
        connection.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s
              AND pid <> pg_backend_pid()
            """,
            (name,),
        )

    def _drop_database(self, connection, name: str) -> None:
        if not self._database_exists(connection, name):
            return

        self._terminate_connections(connection, name)

        connection.execute(
            sql.SQL("DROP DATABASE {}").format(
                sql.Identifier(name)
            )
        )

    def _rename_database(
        self,
        connection,
        old_name: str,
        new_name: str,
    ) -> None:
        self._terminate_connections(connection, old_name)

        connection.execute(
            sql.SQL("ALTER DATABASE {} RENAME TO {}").format(
                sql.Identifier(old_name),
                sql.Identifier(new_name),
            )
        )

    def _create_candidate_database(self, candidate: str) -> None:
        with self._admin_connection() as connection:
            self._drop_database(connection, candidate)

            connection.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(candidate),
                    sql.Identifier(self.db_user),
                )
            )

    def _restore_dump(
        self,
        dump_path: Path,
        candidate: str,
    ) -> None:
        environment = os.environ.copy()
        environment["PGPASSWORD"] = self.db_password

        self._log(f"Restore nel database temporaneo {candidate}...")

        subprocess.run(
            [
                "pg_restore",
                "--host",
                self.db_host,
                "--port",
                str(self.db_port),
                "--username",
                self.db_user,
                "--dbname",
                candidate,
                "--no-owner",
                "--no-privileges",
                "--exit-on-error",
                str(dump_path),
            ],
            env=environment,
            check=True,
        )

    def _validate_database(self, name: str) -> None:
        with psycopg.connect(
            **self._connection_kwargs(name)
        ) as connection:
            connection.execute("SELECT 1").fetchone()

            table_count = connection.execute(
                """
                SELECT count(*)
                FROM pg_catalog.pg_class c
                JOIN pg_catalog.pg_namespace n
                  ON n.oid = c.relnamespace
                WHERE c.relkind IN ('r', 'p')
                  AND n.nspname NOT IN (
                      'pg_catalog',
                      'information_schema'
                  )
                  AND n.nspname NOT LIKE 'pg_toast%%'
                """
            ).fetchone()[0]

            if table_count == 0:
                raise RuntimeError(
                    f"Il database {name} non contiene tabelle utente"
                )

        self._log(
            f"Database {name} validato ({table_count} tabelle utente)."
        )

    # ------------------------------------------------------------------
    # Switch sicuro
    # ------------------------------------------------------------------

    def _switch_database(
        self,
        candidate: str,
        snapshot_version: str,
    ) -> None:
        previous = f"{self.db_name}_previous"

        self.maintenance.set()

        try:
            self._log("Avvio switch del database...")

            with self._admin_connection() as connection:
                self._drop_database(connection, previous)

                if self._database_exists(connection, self.db_name):
                    self._rename_database(
                        connection,
                        self.db_name,
                        previous,
                    )

                self._rename_database(
                    connection,
                    candidate,
                    self.db_name,
                )

            try:
                self._validate_database(self.db_name)

            except Exception:
                self._log(
                    "Validazione del nuovo database fallita. "
                    "Avvio rollback..."
                )

                with self._admin_connection() as connection:
                    self._drop_database(
                        connection,
                        self.db_name,
                    )

                    if self._database_exists(connection, previous):
                        self._rename_database(
                            connection,
                            previous,
                            self.db_name,
                        )

                raise

            self.write_local_version(snapshot_version)

            with self._admin_connection() as connection:
                self._drop_database(connection, previous)

            self._log(
                f"Database aggiornato con successo a {snapshot_version}."
            )

        finally:
            self.maintenance.clear()

    # ------------------------------------------------------------------
    # Ciclo di aggiornamento
    # ------------------------------------------------------------------

    def update_once(self) -> None:
        if not self.enabled:
            return

        if not self._update_lock.acquire(blocking=False):
            self._log("Un aggiornamento è già in corso.")
            return

        dump_path: Path | None = None
        candidate = f"{self.db_name}_candidate"

        try:
            latest = self.get_latest_snapshot()
            local = self.read_local_version()

            self._log(
                f"Versione locale: {local or 'non registrata'}"
            )
            self._log(
                f"Latest disponibile: {latest.version}"
            )

            if not self._needs_update(local, latest.version):
                self._log("Database già aggiornato.")
                return

            self._log(
                f"Nuovo snapshot disponibile: {latest.version}"
            )

            dump_path = self.download_snapshot(latest)

            self._create_candidate_database(candidate)
            self._restore_dump(dump_path, candidate)
            self._validate_database(candidate)

            self._switch_database(
                candidate,
                latest.version,
            )

        except Exception as exc:
            self._log(f"ERRORE aggiornamento: {exc}")

            # Se il candidate esiste ancora, viene rimosso.
            try:
                with self._admin_connection() as connection:
                    self._drop_database(
                        connection,
                        candidate,
                    )
            except Exception as cleanup_error:
                self._log(
                    "Impossibile rimuovere il database temporaneo: "
                    f"{cleanup_error}"
                )

        finally:
            if dump_path is not None:
                dump_path.unlink(missing_ok=True)

            self._update_lock.release()

    async def _update_loop(self) -> None:
        if self.start_delay > 0:
            await asyncio.sleep(self.start_delay)

        while True:
            await asyncio.to_thread(self.update_once)

            await asyncio.sleep(self.interval)

    async def start(self) -> None:
        if not self.enabled:
            self._log("Aggiornamenti automatici disabilitati.")
            return

        self._log(
            "Aggiornamenti automatici attivi "
            f"(intervallo: {self.interval}s)."
        )

        self._task = asyncio.create_task(
            self._update_loop()
        )

    async def stop(self) -> None:
        if self._task is None:
            return

        self._task.cancel()

        try:
            await self._task
        except asyncio.CancelledError:
            pass

        self._task = None


def install_snapshot_updater(app: FastAPI) -> SnapshotUpdater:
    updater = SnapshotUpdater()

    @app.middleware("http")
    async def snapshot_update_middleware(
        request: FastAPIRequest,
        call_next,
    ):
        if updater.maintenance.is_set():
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Database update in progress"
                },
                headers={"Retry-After": "5"},
            )

        return await call_next(request)

    @app.on_event("startup")
    async def start_snapshot_updater() -> None:
        await updater.start()

    @app.on_event("shutdown")
    async def stop_snapshot_updater() -> None:
        await updater.stop()

    app.state.snapshot_updater = updater

    return updater
