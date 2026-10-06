import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from prowlarr import ProwlarrError
from settings import SettingsStore
from version import APP_VERSION
from webapi import create_webapi_router


class FakeUpdater:
    def __init__(self):
        self.reconfigured = 0

    def reconfigure(self):
        self.reconfigured += 1

    def status(self):
        return {
            "installed_version": "db-2026-01-01",
            "latest_version": "db-2026-02-01",
            "enabled": True,
            "updating": False,
            "maintenance": False,
            "last_check": None,
            "next_check": None,
            "last_error": None,
        }


class FakeProwlarr:
    def __init__(self, settings, *, fail=False, existing=False):
        self.settings = settings
        self.fail = fail
        self.existing = existing

    def status(self):
        return {
            "configured": bool(self.settings["url"] and self.settings["api_key"]),
            "connected": not self.fail,
            "indexer_installed": self.existing,
            "error": "Prowlarr is unavailable" if self.fail else None,
        }

    def test_connection(self):
        if self.fail:
            raise ProwlarrError("Prowlarr is unavailable")

    def ensure_indexer(self):
        if self.fail:
            raise ProwlarrError("Prowlarr rejected the indexer")
        return {
            "created": not self.existing,
            "already_installed": self.existing,
            "indexer_id": None if self.existing else 7,
        }


@pytest.fixture
def web_client(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.json", environ={})
    settings = store.load()
    settings["prowlarr"] = {
        "url": "http://prowlarr:9696",
        "indexer_url": "http://icvdb-torznab:8000/api",
        "api_key": "never-return-this",
    }
    store.save(settings)
    app = FastAPI(version=APP_VERSION)
    app.state.settings_store = store
    app.state.snapshot_updater = FakeUpdater()
    app.state.database_probe = lambda: True
    app.state.prowlarr_factory = lambda values: FakeProwlarr(values)
    app.include_router(create_webapi_router())
    return TestClient(app), app


def test_status_contains_stable_health_summary_without_secrets(web_client):
    client, _ = web_client

    response = client.get("/webapi/status")

    assert response.status_code == 200
    assert response.json()["api_version"] == 1
    assert response.json()["application_version"] == APP_VERSION
    assert response.json()["database"]["connected"] is True
    assert response.json()["result_processing"] == {"preset": "unfiltered", "custom_rule_count": 0}
    assert response.json()["prowlarr"] == {
        "configured": True,
        "connected": None,
        "indexer_installed": None,
        "error": None,
    }
    assert "never-return-this" not in response.text


def test_status_reports_database_failure_without_calling_prowlarr(web_client):
    client, app = web_client
    app.state.database_probe = lambda: False
    calls = []

    def fail_if_called(values):
        calls.append(values)
        raise AssertionError("aggregate status called Prowlarr")

    app.state.prowlarr_factory = fail_if_called

    body = client.get("/webapi/status").json()

    assert body["database"]["connected"] is False
    assert body["prowlarr"]["connected"] is None
    assert calls == []


def test_get_and_put_settings_mask_secret_and_reconfigure_updater(web_client):
    client, app = web_client
    public = client.get("/webapi/settings").json()
    assert public["prowlarr"]["api_key_configured"] is True
    assert "api_key" not in public["prowlarr"]

    public["database_update"]["interval_seconds"] = 3600
    response = client.put("/webapi/settings", json=public)

    assert response.status_code == 200
    assert response.json()["database_update"]["interval_seconds"] == 3600
    assert app.state.snapshot_updater.reconfigured == 1
    assert "never-return-this" not in response.text


def test_put_settings_returns_422_for_invalid_or_unknown_input(web_client):
    client, _ = web_client
    settings = client.get("/webapi/settings").json()
    settings["database_update"]["interval_seconds"] = 1
    assert client.put("/webapi/settings", json=settings).status_code == 422

    settings = client.get("/webapi/settings").json()
    settings["unknown"] = True
    assert client.put("/webapi/settings", json=settings).status_code == 422


def test_result_processing_get_and_put_are_focused(web_client):
    client, _ = web_client
    assert client.get("/webapi/result-processing").json() == {
        "preset": "unfiltered",
        "custom_rules": [],
    }

    response = client.put(
        "/webapi/result-processing",
        json={"preset": "italian_preferred", "custom_rules": []},
    )
    assert response.status_code == 200
    assert response.json()["preset"] == "italian_preferred"
    assert (
        client.put(
            "/webapi/result-processing",
            json={"preset": "unknown", "custom_rules": []},
        ).status_code
        == 422
    )


def test_prowlarr_status_test_and_idempotent_add(web_client):
    client, app = web_client
    assert client.get("/webapi/prowlarr/status").json()["connected"] is True
    assert client.get("/webapi/status").json()["prowlarr"] == {
        "configured": True,
        "connected": True,
        "indexer_installed": False,
        "error": None,
    }
    assert client.post("/webapi/prowlarr/test").json() == {"connected": True, "error": None}
    assert client.post("/webapi/prowlarr/indexer").json() == {
        "created": True,
        "already_installed": False,
        "indexer_id": 7,
    }

    app.state.prowlarr_factory = lambda values: FakeProwlarr(values, existing=True)
    assert client.post("/webapi/prowlarr/indexer").json()["already_installed"] is True
    assert client.get("/webapi/status").json()["prowlarr"]["indexer_installed"] is True


def test_prowlarr_errors_are_400_when_unconfigured_and_502_when_remote_fails(web_client):
    client, app = web_client
    settings = app.state.settings_store.load_persisted()
    settings["prowlarr"]["url"] = ""
    app.state.settings_store.save(settings)
    assert client.post("/webapi/prowlarr/test").status_code == 400

    settings["prowlarr"]["url"] = "http://prowlarr:9696"
    app.state.settings_store.save(settings)
    app.state.prowlarr_factory = lambda values: FakeProwlarr(values, fail=True)
    response = client.post("/webapi/prowlarr/indexer")
    assert response.status_code == 502
    assert "never-return-this" not in response.text


def test_prowlarr_error_body_removes_secret_and_traceback_text(web_client):
    client, app = web_client

    class UnsafeProwlarr(FakeProwlarr):
        def test_connection(self):
            raise ProwlarrError(
                "never-return-this\nTraceback (most recent call last): secret details"
            )

    app.state.prowlarr_factory = lambda values: UnsafeProwlarr(values)

    response = client.post("/webapi/prowlarr/test")

    assert response.status_code == 502
    assert response.json() == {"detail": "Prowlarr request failed"}
    assert "never-return-this" not in response.text
    assert "Traceback" not in response.text
