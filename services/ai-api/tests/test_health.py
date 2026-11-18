import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings, load_settings
from app.main import create_app
from app.schemas.health import HealthResponse


def make_client(**overrides: object) -> TestClient:
    values = {"version": "0.1.0", "environment": "local", "docs_enabled": True}
    values.update(overrides)
    return TestClient(create_app(Settings(**values)))


def test_live_returns_typed_health_payload() -> None:
    response = make_client().get("/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ai-api", "version": "0.1.0"}
    HealthResponse.model_validate(response.json())


def test_live_reports_configured_version() -> None:
    response = make_client(version="1.2.3").get("/v1/health/live")

    assert response.json()["version"] == "1.2.3"


def test_live_rejects_writes() -> None:
    assert make_client().post("/v1/health/live").status_code == 405


def test_health_schema_rejects_unexpected_values() -> None:
    with pytest.raises(ValidationError):
        HealthResponse.model_validate({"status": "degraded", "service": "ai-api", "version": "x"})
    with pytest.raises(ValidationError):
        HealthResponse.model_validate(
            {"status": "ok", "service": "ai-api", "version": "x", "extra": True}
        )


def test_openapi_documents_the_health_route_locally() -> None:
    schema = make_client().get("/openapi.json").json()

    assert "/v1/health/live" in schema["paths"]


def test_docs_are_disabled_outside_local() -> None:
    client = make_client(environment="production", docs_enabled=False)

    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_settings_enable_docs_only_for_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LEDGERLENS_ENV", "production")
    assert load_settings().docs_enabled is False

    monkeypatch.setenv("LEDGERLENS_ENV", "local")
    assert load_settings().docs_enabled is True
