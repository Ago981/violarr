from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app as app_module


def make_dist(tmp_path):
    dist = tmp_path / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text(
        '<!doctype html><html><body><div id="app">WebUI</div></body></html>',
        encoding="utf-8",
    )
    (assets / "index-a1b2c3.js").write_text("console.log('webui')", encoding="utf-8")
    return dist


def frontend_client(dist):
    application = FastAPI()

    @application.get("/api")
    def api():
        return {"api": True}

    @application.get("/webapi/status")
    def webapi_status():
        return {"status": "ok"}

    app_module.install_frontend(application, dist)
    return TestClient(application)


def test_missing_assets_do_not_break_import_or_api(tmp_path):
    application = FastAPI()

    @application.get("/api")
    def api():
        return {"api": True}

    assert app_module.install_frontend(application, tmp_path / "missing") is False
    client = TestClient(application)
    assert client.get("/api").json() == {"api": True}
    assert client.get("/").status_code == 404


def test_root_vue_routes_head_and_hashed_assets_are_served(tmp_path):
    client = frontend_client(make_dist(tmp_path))

    root = client.get("/", headers={"accept": "text/html"})
    route = client.get("/settings/results", headers={"accept": "text/html"})
    head = client.head("/settings/results", headers={"accept": "text/html"})
    asset = client.get("/assets/index-a1b2c3.js")

    assert root.status_code == 200
    assert root.headers["content-type"].startswith("text/html")
    assert route.status_code == 200
    assert route.content == root.content
    assert head.status_code == 200
    assert head.content == b""
    assert asset.status_code == 200
    assert asset.headers["content-type"].startswith("text/javascript")
    assert asset.text == "console.log('webui')"


def test_api_webapi_and_framework_routes_are_not_shadowed(tmp_path):
    client = frontend_client(make_dist(tmp_path))

    assert client.get("/api").json() == {"api": True}
    assert client.get("/webapi/status").json() == {"status": "ok"}
    for path in ("/api/unknown", "/webapi/unknown"):
        response = client.get(path, headers={"accept": "text/html"})
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("application/json")
    assert client.get("/openapi.json").headers["content-type"].startswith("application/json")
    assert "Swagger UI" in client.get("/docs").text
    assert "ReDoc" in client.get("/redoc").text


def test_fallback_rejects_non_html_asset_like_and_unsafe_requests(tmp_path):
    client = frontend_client(make_dist(tmp_path))

    cases = (
        ("/settings/results", {"accept": "application/json"}),
        ("/", {"accept": "application/json"}),
        ("/settings/results", {"accept": "text/html;q=0"}),
        ("/missing.js", {"accept": "text/html"}),
        ("/assets/missing.css", {"accept": "text/html"}),
        ("/..%2Fsecret", {"accept": "text/html"}),
        ("/%2e%2e/secret", {"accept": "text/html"}),
        ("/folder%5Csecret", {"accept": "text/html"}),
    )
    for path, headers in cases:
        response = client.get(path, headers=headers)
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("application/json")

    response = client.post("/settings/results", headers={"accept": "text/html"})
    assert response.status_code == 405
    assert response.headers["content-type"].startswith("application/json")


def test_frontend_path_defaults_to_image_location_and_supports_override(tmp_path, monkeypatch):
    assert app_module.frontend_dist_path({}) == Path("/app/frontend-dist")
    assert app_module.frontend_dist_path({"FRONTEND_DIST_DIR": "/tmp/custom-webui"}) == Path(
        "/tmp/custom-webui"
    )

    dist = make_dist(tmp_path)
    monkeypatch.setenv("FRONTEND_DIST_DIR", str(dist))
    application = FastAPI()
    assert app_module.install_frontend(application) is True
    assert TestClient(application).get("/", headers={"accept": "text/html"}).status_code == 200
