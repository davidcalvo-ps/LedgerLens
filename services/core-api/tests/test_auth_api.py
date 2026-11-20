import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from modules.accounts.models import Membership, Organization, Role

pytestmark = pytest.mark.django_db

PASSWORD = "correct-horse-battery"


@pytest.fixture
def orgs() -> dict[str, Organization]:
    return {
        "a": Organization.objects.create(name="Org A", slug="org-a"),
        "b": Organization.objects.create(name="Org B", slug="org-b"),
    }


@pytest.fixture
def owner_a(orgs):
    user = get_user_model().objects.create_user(
        username="owner@a.example", email="owner@a.example", password=PASSWORD
    )
    Membership.objects.create(organization=orgs["a"], user=user, role=Role.OWNER)
    return user


@pytest.fixture
def csrf_client() -> APIClient:
    return APIClient(enforce_csrf_checks=True)


def fetch_csrf(client: APIClient) -> str:
    response = client.get("/api/v1/auth/csrf")
    assert response.status_code == 204
    return response.cookies["ledgerlens_csrftoken"].value


def sign_in(client: APIClient, email: str = "owner@a.example", password: str = PASSWORD):
    token = fetch_csrf(client)
    return client.post(
        "/api/v1/auth/login",
        {"email": email, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )


def test_login_returns_user_and_memberships(csrf_client, owner_a, orgs) -> None:
    response = sign_in(csrf_client, email="  Owner@A.example ")

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "owner@a.example"
    assert [(m["organization"]["slug"], m["role"]) for m in body["memberships"]] == [
        ("org-a", "owner")
    ]


def test_session_cookie_is_http_only_lax_and_secure(csrf_client, owner_a) -> None:
    response = sign_in(csrf_client)

    cookie = response.cookies["ledgerlens_session"]
    assert cookie["httponly"] is True
    assert cookie["samesite"] == "Lax"
    assert cookie["secure"] is True
    assert int(cookie["max-age"]) == 8 * 60 * 60


def test_login_without_csrf_token_is_rejected(csrf_client, owner_a) -> None:
    response = csrf_client.post(
        "/api/v1/auth/login", {"email": "owner@a.example", "password": PASSWORD}, format="json"
    )

    assert response.status_code == 403
    assert "ledgerlens_session" not in response.cookies


@pytest.mark.parametrize(
    ("email", "password"),
    [("owner@a.example", "wrong-password-123"), ("nobody@a.example", PASSWORD)],
)
def test_bad_credentials_get_one_generic_answer(csrf_client, owner_a, email, password) -> None:
    response = sign_in(csrf_client, email=email, password=password)

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email or password."}


def test_inactive_users_cannot_sign_in(csrf_client, owner_a) -> None:
    owner_a.is_active = False
    owner_a.save()

    assert sign_in(csrf_client).status_code == 400


def test_login_rotates_the_session_key(csrf_client, owner_a) -> None:
    csrf_client.cookies["ledgerlens_session"] = "attacker-chosen-session-id"

    response = sign_in(csrf_client)

    assert response.cookies["ledgerlens_session"].value != "attacker-chosen-session-id"


def test_session_endpoint_requires_sign_in() -> None:
    response = APIClient().get("/api/v1/auth/session")

    # 401, not 403: the web app uses it to tell "expired" from "forbidden".
    assert response.status_code == 401
    assert response["WWW-Authenticate"] == 'Session realm="ledgerlens"'


def test_session_endpoint_returns_current_user(csrf_client, owner_a) -> None:
    sign_in(csrf_client)

    response = csrf_client.get("/api/v1/auth/session")

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "owner@a.example"


def test_logout_needs_csrf_and_ends_the_session(csrf_client, owner_a) -> None:
    sign_in(csrf_client)

    assert csrf_client.post("/api/v1/auth/logout").status_code == 403

    token = csrf_client.cookies["ledgerlens_csrftoken"].value
    assert csrf_client.post("/api/v1/auth/logout", HTTP_X_CSRFTOKEN=token).status_code == 204
    assert csrf_client.get("/api/v1/auth/session").status_code == 401


def test_current_member_returns_role_in_own_organization(csrf_client, owner_a, orgs) -> None:
    sign_in(csrf_client)

    response = csrf_client.get(f"/api/v1/orgs/{orgs['a'].id}/members/me")

    assert response.status_code == 200
    assert response.json()["role"] == "owner"
    assert response.json()["organization"]["id"] == str(orgs["a"].id)


def test_current_member_hides_other_organizations(csrf_client, owner_a, orgs) -> None:
    sign_in(csrf_client)

    other = csrf_client.get(f"/api/v1/orgs/{orgs['b'].id}/members/me")
    missing = csrf_client.get("/api/v1/orgs/00000000-0000-0000-0000-000000000000/members/me")

    assert other.status_code == 404
    assert missing.status_code == 404
    assert other.json() == missing.json()


def test_current_member_requires_sign_in(orgs) -> None:
    assert APIClient().get(f"/api/v1/orgs/{orgs['a'].id}/members/me").status_code == 401
