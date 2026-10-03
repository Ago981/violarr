import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / "Dockerfile"
ENTRYPOINT = ROOT / "entrypoint.sh"


def dockerfile_text():
    return DOCKERFILE.read_text(encoding="utf-8")


def final_stage():
    text = dockerfile_text()
    starts = [match.start() for match in re.finditer(r"(?im)^FROM\s+", text)]
    return text[starts[-1] :]


def logical_instructions(text):
    return re.sub(r"\\\r?\n\s*", " ", text)


def test_entrypoint_is_lf_only_and_keeps_bash_shebang():
    content = ENTRYPOINT.read_bytes()

    assert content.startswith(b"#!/usr/bin/env bash\n")
    assert b"\r" not in content


def test_final_stage_uses_clean_bookworm_runtime_and_pgdg_postgresql_16():
    stage = logical_instructions(final_stage())

    assert re.search(r"(?im)^FROM\s+debian:bookworm-slim(?:\s|$)", stage)
    assert "apt.postgresql.org/pub/repos/apt" in stage
    assert re.search(r"\bpostgresql-16\b", stage)
    assert re.search(r"\bpostgresql-client-16\b", stage)
    assert "/usr/lib/postgresql/16/bin" in stage
    assert "create_main_cluster = false" in stage
    assert "policy-rc.d" in stage
    assert re.search(r"\bgosu\b", stage)
    assert re.search(r"\btini\b", stage)


def test_final_stage_declares_only_product_volume_and_port():
    stage = final_stage()
    exposed = re.findall(r"(?im)^EXPOSE\s+(.+?)\s*$", stage)
    volumes = re.findall(r"(?im)^VOLUME\s+(.+?)\s*$", stage)

    assert exposed == ["8000"]
    assert volumes == ['["/data"]']
    assert "/var/lib/postgresql/data" not in stage
    assert not re.search(r"(?im)^EXPOSE\s+.*\b5432\b", stage)


def test_image_keeps_frontend_build_and_all_runtime_modules():
    text = logical_instructions(dockerfile_text())
    stage = logical_instructions(final_stage())

    assert re.search(r"(?im)^FROM\s+node:24-bookworm-slim\s+AS\s+frontend-build", text)
    assert re.search(r"(?im)^RUN\s+npm\s+ci\s*$", text)
    assert re.search(r"(?im)^RUN\s+npm\s+run\s+build\s*$", text)
    assert "COPY --from=frontend-build /build/frontend/dist /app/frontend-dist" in stage

    for module in (
        "app.py",
        "snapshot_updater.py",
        "settings.py",
        "result_processor.py",
        "prowlarr.py",
        "webapi.py",
        "entrypoint.sh",
    ):
        assert re.search(rf"(?im)^COPY\s+[^\n]*\b{re.escape(module)}\b", stage)


def test_runtime_defaults_keep_data_layout_without_baking_password():
    stage = logical_instructions(final_stage())

    assert re.search(r'\bPGDATA="?/data/postgres"?', stage)
    assert re.search(r'\bSNAPSHOT_STATE_FILE="?/data/state/snapshot-version"?', stage)
    assert not re.search(r"(?im)^ENV\s+[^\n]*\bDB_PASSWORD=", stage)
