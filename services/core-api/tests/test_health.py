import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from modules.health import checks


@pytest.fixture
def client() -> APIClient:
    return APIClient()


def set_probes(monkeypatch: pytest.MonkeyPatch, **results: bool) -> None:
    probes = {name: (lambda ok=ok: ok) for name, ok in results.items()}
    monkeypatch.setattr(checks, "PROBES", probes)


def test_liveness_reports_service_and_version(client: APIClient) -> None:
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert response.json() == {"status": "ok", "service": "core-api", "version": "0.1.0"}


def test_health_routes_are_versioned() -> None:
    assert reverse("health:live") == "/api/v1/health/live"
    assert reverse("health:ready") == "/api/v1/health/ready"


def test_liveness_needs_no_credentials_but_rejects_writes(client: APIClient) -> None:
    assert client.post("/api/v1/health/live", {}, format="json").status_code == 405


def test_readiness_ok_when_all_dependencies_respond(
    client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_probes(monkeypatch, database=True, redis=True)

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["checks"] == {"database": "ok", "redis": "ok"}


@pytest.mark.parametrize(
    ("database", "redis", "expected"),
    [
        (False, True, {"database": "failing", "redis": "ok"}),
        (True, False, {"database": "ok", "redis": "failing"}),
        (False, False, {"database": "failing", "redis": "failing"}),
    ],
)
def test_readiness_returns_503_when_a_dependency_fails(
    client: APIClient,
    monkeypatch: pytest.MonkeyPatch,
    database: bool,
    redis: bool,
    expected: dict[str, str],
) -> None:
    set_probes(monkeypatch, database=database, redis=redis)

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["checks"] == expected


@pytest.mark.django_db
def test_database_probe_runs_a_real_query() -> None:
    assert checks.database_ok() is True


def test_redis_probe_reports_failure_without_raising() -> None:
    # Test settings point at a port where nothing listens.
    assert checks.redis_ok() is False


def test_unknown_routes_return_404(client: APIClient) -> None:
    assert client.get("/api/v1/unknown").status_code == 404
