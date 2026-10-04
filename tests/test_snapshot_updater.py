import asyncio
import hashlib
import io
import json
from datetime import datetime, timezone
import threading

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from settings import SettingsStore
from snapshot_updater import Snapshot, SnapshotUpdater, install_snapshot_updater


def make_store(tmp_path, environ=None):
    return SettingsStore(path=tmp_path / "settings.json", environ=environ or {})


def test_snapshot_requests_use_versioned_violarr_user_agent(tmp_path, monkeypatch):
    metadata = {
        "tag_name": "db-2026-10-05",
        "assets": [
            {
                "name": "snapshot.dump",
                "browser_download_url": "https://example/snapshot.dump",
                "digest": f"sha256:{hashlib.sha256(b'dump').hexdigest()}",
            }
        ],
    }
    responses = [json.dumps(metadata).encode(), b"dump"]
    requests = []

    def urlopen(request, timeout):
        requests.append(request)
        return io.BytesIO(responses.pop(0))

    monkeypatch.setattr("snapshot_updater.urlopen", urlopen)
    monkeypatch.setattr("snapshot_updater.subprocess.run", lambda *args, **kwargs: None)
    updater = SnapshotUpdater(settings_store=make_store(tmp_path))

    snapshot = updater.get_latest_snapshot()
    path = updater.download_snapshot(snapshot)
    path.unlink()

    assert [request.get_header("User-agent") for request in requests] == [
        "Violarr/1.1.0",
        "Violarr/1.1.0",
    ]


def test_updater_reads_effective_store_settings_and_runtime_reconfigure(tmp_path):
    store = make_store(tmp_path)
    settings = store.load()
    settings["database_update"] = {"enabled": False, "interval_seconds": 3600}
    store.save(settings)
    updater = SnapshotUpdater(settings_store=store)
    wake = threading.Event()
    updater._signal_wake = wake.set

    assert updater.status()["enabled"] is False
    assert updater.interval == 3600

    settings["database_update"] = {"enabled": True, "interval_seconds": 120}
    store.save(settings)
    updater.reconfigure()

    assert updater.status()["enabled"] is True
    assert updater.interval == 120
    assert wake.is_set()


def test_updater_environment_precedence_remains_effective(tmp_path):
    store = make_store(
        tmp_path,
        {"DB_AUTO_UPDATE": "false", "DB_UPDATE_INTERVAL": "7200"},
    )
    updater = SnapshotUpdater(settings_store=store)

    assert updater.status()["enabled"] is False
    assert updater.interval == 7200
    assert store.load_persisted()["database_update"]["enabled"] is True


def test_update_status_transitions_and_failure_is_sanitized(tmp_path, monkeypatch):
    updater = SnapshotUpdater(settings_store=make_store(tmp_path))
    updater.state_file = tmp_path / "snapshot-version"
    monkeypatch.setattr(
        updater,
        "get_latest_snapshot",
        lambda: (_ for _ in ()).throw(RuntimeError("password=do-not-return")),
    )
    monkeypatch.setattr(updater, "_admin_connection", lambda: (_ for _ in ()).throw(OSError()))

    updater.update_once()
    status = updater.status()

    assert status["updating"] is False
    assert status["last_check"] is not None
    assert status["last_error"] == "Snapshot update failed"
    assert "do-not-return" not in json.dumps(status)


def test_success_updates_latest_and_installed_status_without_changing_switch(tmp_path, monkeypatch):
    updater = SnapshotUpdater(settings_store=make_store(tmp_path))
    updater.state_file = tmp_path / "snapshot-version"
    updater.write_local_version("db-2026-01-01")
    snapshot = Snapshot("db-2026-02-01", "snapshot.dump", "https://example/dump", "sha256:x")
    dump = tmp_path / "download.dump"
    dump.write_bytes(b"dump")
    calls = []
    monkeypatch.setattr(updater, "get_latest_snapshot", lambda: snapshot)
    monkeypatch.setattr(updater, "download_snapshot", lambda value: dump)
    monkeypatch.setattr(updater, "_create_candidate_database", lambda value: calls.append("create"))
    monkeypatch.setattr(updater, "_restore_dump", lambda *args: calls.append("restore"))
    monkeypatch.setattr(updater, "_validate_database", lambda value: calls.append("validate"))

    def switch(candidate, version):
        calls.append("switch")
        updater.write_local_version(version)

    monkeypatch.setattr(updater, "_switch_database", switch)

    updater.update_once()
    status = updater.status()

    assert calls == ["create", "restore", "validate", "switch"]
    assert status["installed_version"] == "db-2026-02-01"
    assert status["latest_version"] == "db-2026-02-01"
    assert status["last_error"] is None


def test_reconfigure_wakes_disabled_periodic_loop_without_concurrent_update(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    settings = store.load()
    settings["database_update"]["enabled"] = False
    store.save(settings)
    updater = SnapshotUpdater(settings_store=store)
    updater.start_delay = 0
    calls = []
    monkeypatch.setattr(updater, "update_once", lambda: calls.append("update"))

    async def scenario():
        await updater.start()
        await asyncio.sleep(0.01)
        assert calls == []
        settings["database_update"] = {"enabled": True, "interval_seconds": 60}
        store.save(settings)
        updater.reconfigure()
        await asyncio.sleep(0.05)
        await updater.stop()

    asyncio.run(scenario())
    assert calls == ["update"]


def test_status_has_next_check_only_when_enabled(tmp_path):
    updater = SnapshotUpdater(settings_store=make_store(tmp_path))
    updater._set_next_check(datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert updater.status()["next_check"] == "2026-01-01T00:00:00+00:00"

    settings = updater.settings_store.load_persisted()
    settings["database_update"]["enabled"] = False
    updater.settings_store.save(settings)
    updater.reconfigure()
    assert updater.status()["next_check"] is None


def test_update_lock_prevents_concurrent_snapshot_checks(tmp_path, monkeypatch):
    updater = SnapshotUpdater(settings_store=make_store(tmp_path))
    calls = []
    monkeypatch.setattr(updater, "get_latest_snapshot", lambda: calls.append("network"))
    updater._update_lock.acquire()
    try:
        updater.update_once()
    finally:
        updater._update_lock.release()

    assert calls == []
    assert updater.status()["updating"] is False


def test_status_observes_maintenance_without_network_access(tmp_path, monkeypatch):
    updater = SnapshotUpdater(settings_store=make_store(tmp_path))
    monkeypatch.setattr(
        updater,
        "get_latest_snapshot",
        lambda: (_ for _ in ()).throw(AssertionError("network called")),
    )
    updater.maintenance.set()

    assert updater.status()["maintenance"] is True


def test_concurrent_reconfigure_and_stop_are_lifecycle_safe(tmp_path):
    store = make_store(tmp_path)
    settings = store.load()
    settings["database_update"]["enabled"] = False
    store.save(settings)
    updater = SnapshotUpdater(settings_store=store)
    updater.start_delay = 0
    signal_started = threading.Event()
    release_signal = threading.Event()
    errors = []

    class ClosingLoop:
        def call_soon_threadsafe(self, callback):
            signal_started.set()
            release_signal.wait()
            raise RuntimeError("event loop is closed")

    def reconfigure():
        try:
            updater.reconfigure()
        except Exception as exc:
            errors.append(exc)

    async def scenario():
        await updater.start()
        with updater._lifecycle_lock:
            updater._loop = ClosingLoop()
        worker = threading.Thread(target=reconfigure)
        worker.start()
        await asyncio.to_thread(signal_started.wait)
        stop_task = asyncio.create_task(updater.stop())
        release_signal.set()
        await stop_task
        await asyncio.to_thread(worker.join)

    asyncio.run(scenario())

    assert errors == []
    with updater._lifecycle_lock:
        assert updater._task is None
        assert updater._loop is None
        assert updater._wake_event is None


def test_maintenance_middleware_returns_stable_503(tmp_path):
    app = FastAPI()
    updater = install_snapshot_updater(app, make_store(tmp_path))

    @app.get("/probe")
    def probe():
        return {"ok": True}

    updater.maintenance.set()
    response = TestClient(app).get("/probe")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database update in progress"}
    assert response.headers["Retry-After"] == "5"

    updater.maintenance.clear()
    assert TestClient(app).get("/probe").json() == {"ok": True}


def test_candidate_switch_rolls_back_after_new_database_validation_failure(
    tmp_path, monkeypatch
):
    updater = SnapshotUpdater(settings_store=make_store(tmp_path))
    updater.db_name = "icv_db"
    calls = []

    class Connection:
        def __init__(self, phase):
            self.phase = phase

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    connections = iter([Connection("switch"), Connection("rollback")])
    monkeypatch.setattr(updater, "_admin_connection", lambda: next(connections))
    monkeypatch.setattr(
        updater,
        "_database_exists",
        lambda connection, name: name
        == ("icv_db" if connection.phase == "switch" else "icv_db_previous"),
    )
    monkeypatch.setattr(
        updater,
        "_drop_database",
        lambda connection, name: calls.append((connection.phase, "drop", name)),
    )
    monkeypatch.setattr(
        updater,
        "_rename_database",
        lambda connection, old, new: calls.append(
            (connection.phase, "rename", old, new)
        ),
    )
    monkeypatch.setattr(
        updater,
        "_validate_database",
        lambda name: (_ for _ in ()).throw(RuntimeError("invalid candidate")),
    )
    monkeypatch.setattr(
        updater,
        "write_local_version",
        lambda version: calls.append(("unexpected-version-write", version)),
    )

    with pytest.raises(RuntimeError, match="invalid candidate"):
        updater._switch_database("icv_db_candidate", "db-2026-02-01")

    assert calls == [
        ("switch", "drop", "icv_db_previous"),
        ("switch", "rename", "icv_db", "icv_db_previous"),
        ("switch", "rename", "icv_db_candidate", "icv_db"),
        ("rollback", "drop", "icv_db"),
        ("rollback", "rename", "icv_db_previous", "icv_db"),
    ]
    assert updater.maintenance.is_set() is False
