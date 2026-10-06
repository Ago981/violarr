import json
import socket
from copy import deepcopy
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

DEFAULT_TIMEOUT = 10.0
DEFAULT_MAX_RESPONSE_BYTES = 1024 * 1024
PROWLARR_SCHEMA_MAX_RESPONSE_BYTES = 16 * 1024 * 1024


class ProwlarrError(RuntimeError):
    """A secret-safe error suitable for an API response."""


def _absolute_http_url(value: str, name: str) -> tuple[str, str, str]:
    try:
        parsed = urlsplit(value)
        parsed.port
    except (TypeError, ValueError) as exc:
        raise ProwlarrError(f"{name} is not a valid HTTP URL") from exc
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ProwlarrError(f"{name} is not a valid HTTP URL")
    origin = urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
    return origin, parsed.path, parsed.query


def normalize_base_url(value: str) -> str:
    origin, path, query = _absolute_http_url(value, "Prowlarr URL")
    parsed = urlsplit(value)
    if query or parsed.fragment:
        raise ProwlarrError("Prowlarr URL must not include a query or fragment")
    suffix = path.rstrip("/")
    return f"{origin}{suffix}"


def split_indexer_url(value: str) -> tuple[str, str]:
    origin, path, query = _absolute_http_url(value, "Indexer URL")
    parsed = urlsplit(value)
    if query or parsed.fragment:
        raise ProwlarrError("Indexer URL must not include a query or fragment")
    api_path = f"/{path.lstrip('/')}" if path not in {"", "/"} else "/api"
    return origin, api_path


def _field_values(resource: dict[str, Any]) -> dict[str, Any]:
    fields = resource.get("fields")
    if not isinstance(fields, list):
        return {}
    return {
        field.get("name"): field.get("value")
        for field in fields
        if isinstance(field, dict) and isinstance(field.get("name"), str)
    }


class ProwlarrClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        indexer_url: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        self.base_url = normalize_base_url(base_url)
        self.api_key = api_key
        self.indexer_url = indexer_url
        self.timeout = min(max(float(timeout), 0.1), 30.0)
        self.max_response_bytes = max_response_bytes
        self._opener = opener

    def _request(
        self,
        method: str,
        path: str,
        payload: Any = None,
        max_response_bytes: int | None = None,
    ) -> Any:
        effective_max_response_bytes = (
            self.max_response_bytes if max_response_bytes is None else max_response_bytes
        )
        body = None
        headers = {
            "Accept": "application/json",
            "X-Api-Key": self.api_key,
        }
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with self._opener(request, timeout=self.timeout) as response:
                length = response.headers.get("Content-Length")
                if length is not None:
                    try:
                        if int(length) > effective_max_response_bytes:
                            raise ProwlarrError("Prowlarr response is too large")
                    except ValueError:
                        pass
                raw = response.read(effective_max_response_bytes + 1)
        except HTTPError as exc:
            raise ProwlarrError(f"Prowlarr returned HTTP {exc.code}") from None
        except (URLError, OSError, socket.timeout, TimeoutError):
            raise ProwlarrError("Unable to connect to Prowlarr") from None

        if len(raw) > effective_max_response_bytes:
            raise ProwlarrError("Prowlarr response is too large")
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ProwlarrError("Prowlarr returned invalid JSON") from None

    def _schemas(self) -> list[dict[str, Any]]:
        payload = self._request(
            "GET",
            "/api/v1/indexer/schema",
            max_response_bytes=PROWLARR_SCHEMA_MAX_RESPONSE_BYTES,
        )
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise ProwlarrError("Prowlarr returned an invalid indexer schema response")
        return payload

    def test_connection(self) -> None:
        self._schemas()

    def _generic_template(self) -> dict[str, Any]:
        for resource in self._schemas():
            if resource.get("implementation") != "Torznab":
                continue
            name = str(resource.get("name", "")).casefold()
            implementation_name = str(resource.get("implementationName", "")).casefold()
            if name == "generic torznab" or implementation_name == "generic torznab":
                return resource
        raise ProwlarrError("Prowlarr Generic Torznab schema is unavailable")

    def build_indexer_resource(self) -> dict[str, Any]:
        resource = deepcopy(self._generic_template())

        base_url, api_path = split_indexer_url(self.indexer_url)

        values = {
            "baseUrl": base_url,
            "apiPath": api_path,
            "apiKey": "",
        }

        fields = resource.get("fields")

        if not isinstance(fields, list):
            raise ProwlarrError("Prowlarr Generic Torznab schema has invalid fields")

        found = set()

        for field in fields:
            if isinstance(field, dict) and field.get("name") in values:
                field["value"] = values[field["name"]]
                found.add(field["name"])

        missing = set(values) - found

        if missing:
            missing_name = sorted(missing)[0]
            raise ProwlarrError(f"Prowlarr Generic Torznab schema is missing {missing_name}")

        resource["name"] = "Violarr"
        resource["appProfileId"] = self._default_app_profile_id()

        return resource

    def _indexers(self) -> list[dict[str, Any]]:
        payload = self._request("GET", "/api/v1/indexer")
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise ProwlarrError("Prowlarr returned an invalid indexer list")
        return payload

    def _is_installed(self, resource: dict[str, Any]) -> bool:
        if resource.get("implementation") != "Torznab":
            return False
        fields = _field_values(resource)
        try:
            configured = split_indexer_url(self.indexer_url)
            existing_origin, existing_path = split_indexer_url(
                f"{str(fields.get('baseUrl', '')).rstrip('/')}/{str(fields.get('apiPath', '')).lstrip('/')}"
            )
        except ProwlarrError:
            return False
        return (existing_origin.rstrip("/"), existing_path.rstrip("/")) == (
            configured[0].rstrip("/"),
            configured[1].rstrip("/"),
        )

    def ensure_indexer(self) -> dict[str, Any]:
        resource = self.build_indexer_resource()
        existing = next((item for item in self._indexers() if self._is_installed(item)), None)
        if existing is not None:
            identifier = existing.get("id")
            return {
                "created": False,
                "already_installed": True,
                "indexer_id": identifier if isinstance(identifier, int) else None,
            }
        self._request("POST", "/api/v1/indexer/test", resource)
        created = self._request("POST", "/api/v1/indexer", resource)
        identifier = created.get("id") if isinstance(created, dict) else None
        return {
            "created": True,
            "already_installed": False,
            "indexer_id": identifier if isinstance(identifier, int) else None,
        }

    def status(self) -> dict[str, Any]:
        try:
            self.test_connection()
            installed = any(self._is_installed(item) for item in self._indexers())
            return {
                "configured": True,
                "connected": True,
                "indexer_installed": installed,
                "error": None,
            }
        except ProwlarrError as exc:
            return {
                "configured": True,
                "connected": False,
                "indexer_installed": False,
                "error": str(exc),
            }

    def _app_profiles(self) -> list[dict[str, Any]]:
        payload = self._request("GET", "/api/v1/appprofile")

        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise ProwlarrError("Prowlarr returned an invalid app profile response")

        return payload

    def _default_app_profile_id(self) -> int:
        profiles = self._app_profiles()

        for profile in profiles:
            profile_id = profile.get("id")

            if isinstance(profile_id, int) and not isinstance(profile_id, bool) and profile_id > 0:
                return profile_id

        raise ProwlarrError("Prowlarr has no valid app profile configured")
