import json
from urllib.error import HTTPError

import pytest

from prowlarr import ProwlarrClient, ProwlarrError, split_indexer_url


class Response:
    def __init__(self, payload, status=200, headers=None):
        self.body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.status = status
        self.headers = headers or {}
        self.offset = 0

    def read(self, size=-1):
        if size < 0:
            size = len(self.body) - self.offset
        chunk = self.body[self.offset : self.offset + size]
        self.offset += len(chunk)
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append((request, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def generic_schema():
    return {
        "name": "Generic Torznab",
        "implementationName": "Torznab",
        "implementation": "Torznab",
        "enable": True,
        "priority": 25,
        "appProfileId": 1,
        "fields": [
            {"name": "baseUrl", "value": "", "type": "textbox"},
            {"name": "apiPath", "value": "/api", "type": "textbox"},
            {"name": "apiKey", "value": "", "type": "textbox"},
            {"name": "seedCriteria", "value": {"seeders": 1}},
        ],
    }


def client(responses, *, max_response_bytes=1024 * 1024):
    opener = FakeOpener(responses)
    return (
        ProwlarrClient(
            "http://prowlarr:9696/",
            "secret-key",
            "http://icvdb-torznab:8000/api",
            opener=opener,
            max_response_bytes=max_response_bytes,
        ),
        opener,
    )


def test_connection_uses_authenticated_schema_endpoint():
    subject, opener = client([Response([generic_schema()])])

    subject.test_connection()

    request, timeout = opener.requests[0]
    assert request.full_url == "http://prowlarr:9696/api/v1/indexer/schema"
    assert request.get_header("X-api-key") == "secret-key"
    assert 0 < timeout <= 30


@pytest.mark.parametrize(
    "response",
    [
        Response(b""),
        Response(b"not-json"),
        Response(b"x" * 33, headers={"Content-Length": "33"}),
        Response(b"x" * 33),
    ],
)
def test_invalid_or_oversized_responses_are_rejected(response):
    subject, _ = client([response], max_response_bytes=32)

    with pytest.raises(ProwlarrError):
        subject.test_connection()


def test_http_and_transport_errors_never_expose_api_key():
    error = HTTPError("http://prowlarr", 401, "secret-key", {}, None)
    subject, _ = client([error])

    with pytest.raises(ProwlarrError) as captured:
        subject.test_connection()

    assert "secret-key" not in str(captured.value)
    assert "401" in str(captured.value)


def test_schema_is_deep_copied_and_named_fields_are_updated():
    schema = generic_schema()
    subject, _ = client([Response([schema])])

    resource = subject.build_indexer_resource()

    assert resource["name"] == "ICVDB Torznab"
    assert resource["priority"] == 25
    assert resource["appProfileId"] == 1
    assert {field["name"]: field.get("value") for field in resource["fields"]} == {
        "baseUrl": "http://icvdb-torznab:8000",
        "apiPath": "/api",
        "apiKey": "",
        "seedCriteria": {"seeders": 1},
    }
    assert schema["fields"][0]["value"] == ""


def test_missing_generic_schema_or_required_fields_is_rejected():
    wrong = generic_schema()
    wrong["implementation"] = "Newznab"
    subject, _ = client([Response([wrong])])
    with pytest.raises(ProwlarrError, match="Generic Torznab"):
        subject.build_indexer_resource()

    incomplete = generic_schema()
    incomplete["fields"] = incomplete["fields"][:-1]
    incomplete["fields"] = [f for f in incomplete["fields"] if f["name"] != "apiPath"]
    subject, _ = client([Response([incomplete])])
    with pytest.raises(ProwlarrError, match="apiPath"):
        subject.build_indexer_resource()


def test_existing_indexer_is_detected_by_implementation_and_normalized_endpoint():
    existing = generic_schema()
    existing["name"] = "Renamed by user"
    existing["fields"][0]["value"] = "http://icvdb-torznab:8000/"
    subject, opener = client([Response([generic_schema()]), Response([existing])])

    result = subject.ensure_indexer()

    assert result == {"created": False, "already_installed": True, "indexer_id": None}
    assert len(opener.requests) == 2


def test_create_tests_resource_before_posting_and_preserves_template_defaults():
    subject, opener = client(
        [Response([generic_schema()]), Response([]), Response({}), Response({"id": 42})]
    )

    result = subject.ensure_indexer()

    assert result == {"created": True, "already_installed": False, "indexer_id": 42}
    assert [request.method for request, _ in opener.requests] == ["GET", "GET", "POST", "POST"]
    assert [request.full_url for request, _ in opener.requests][-2:] == [
        "http://prowlarr:9696/api/v1/indexer/test",
        "http://prowlarr:9696/api/v1/indexer",
    ]
    tested = json.loads(opener.requests[-2][0].data)
    created = json.loads(opener.requests[-1][0].data)
    assert tested == created
    assert created["appProfileId"] == 1


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://host:8000/api", ("http://host:8000", "/api")),
        ("https://host/root/api/", ("https://host", "/root/api/")),
        ("https://host", ("https://host", "/api")),
        ("https://host/", ("https://host", "/api")),
        ("http://[2001:db8::1]:8000/api", ("http://[2001:db8::1]:8000", "/api")),
    ],
)
def test_indexer_url_is_split_into_origin_and_api_path(url, expected):
    assert split_indexer_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://host/root/api?t=caps",
        "https://host/root/api#caps",
    ],
)
def test_indexer_url_rejects_query_and_fragment(url):
    with pytest.raises(ProwlarrError, match="query or fragment"):
        split_indexer_url(url)


def test_status_reports_connection_failure_without_secret():
    subject, _ = client([OSError("failed secret-key")])

    status = subject.status()

    assert status["configured"] is True
    assert status["connected"] is False
    assert status["indexer_installed"] is False
    assert "secret-key" not in json.dumps(status)
