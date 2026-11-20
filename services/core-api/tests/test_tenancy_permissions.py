"""Cross-tenant isolation and the role matrix for organization-scoped APIs.

Two organizations, one person per role in A, plus an outsider who only
belongs to B. Every scoped endpoint is exercised with every caller.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from modules.accounts.models import Membership, Organization, Role

pytestmark = pytest.mark.django_db

User = get_user_model()


def make_user(email: str, **extra):
    return User.objects.create_user(username=email, email=email, password=None, **extra)


@pytest.fixture
def org_a() -> Organization:
    return Organization.objects.create(name="Org A", slug="org-a")


@pytest.fixture
def org_b() -> Organization:
    return Organization.objects.create(name="Org B", slug="org-b")


@pytest.fixture
def people(org_a, org_b) -> dict:
    users = {}
    for role in Role:
        users[role.value] = make_user(f"{role.value}@a.example")
        Membership.objects.create(organization=org_a, user=users[role.value], role=role)
    users["outsider"] = make_user("owner@b.example")
    Membership.objects.create(organization=org_b, user=users["outsider"], role=Role.OWNER)
    return users


def client_for(user) -> APIClient:
    client = APIClient()
    client.force_login(user)
    return client


# (method, path template, payload, expected status per role in org A)
MATRIX = [
    ("get", "/api/v1/orgs/{org}", None, {"owner": 200, "accountant": 200, "analyst": 200}),
    (
        "patch",
        "/api/v1/orgs/{org}",
        {"name": "Renamed"},
        {"owner": 200, "accountant": 403, "analyst": 403},
    ),
    ("get", "/api/v1/orgs/{org}/members", None, {"owner": 200, "accountant": 403, "analyst": 403}),
    (
        "get",
        "/api/v1/orgs/{org}/members/me",
        None,
        {"owner": 200, "accountant": 200, "analyst": 200},
    ),
]

CASES = [
    pytest.param(method, path, payload, role, expected[role], id=f"{method}-{path}-{role}")
    for method, path, payload, expected in MATRIX
    for role in ("owner", "accountant", "analyst")
]


@pytest.mark.parametrize(("method", "path", "payload", "role", "expected"), CASES)
def test_role_matrix(people, org_a, method, path, payload, role, expected) -> None:
    client = client_for(people[role])

    response = getattr(client, method)(path.format(org=org_a.id), payload, format="json")

    assert response.status_code == expected


@pytest.mark.parametrize(("method", "path", "payload", "_role", "_expected"), CASES[::3])
def test_outsider_gets_404_for_every_endpoint(
    people, org_a, method, path, payload, _role, _expected
) -> None:
    client = client_for(people["outsider"])

    response = getattr(client, method)(path.format(org=org_a.id), payload, format="json")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found."}


@pytest.mark.parametrize(("method", "path", "payload", "_role", "_expected"), CASES[::3])
def test_anonymous_gets_401_for_every_endpoint(
    org_a, method, path, payload, _role, _expected
) -> None:
    response = getattr(APIClient(), method)(path.format(org=org_a.id), payload, format="json")

    assert response.status_code == 401


def test_owner_of_a_cannot_rename_b(people, org_b) -> None:
    client = client_for(people["owner"])

    response = client.patch(f"/api/v1/orgs/{org_b.id}", {"name": "Hijacked"}, format="json")

    assert response.status_code == 404
    org_b.refresh_from_db()
    assert org_b.name == "Org B"


def test_owner_of_a_cannot_list_b_members(people, org_b) -> None:
    response = client_for(people["owner"]).get(f"/api/v1/orgs/{org_b.id}/members")

    assert response.status_code == 404
    assert "owner@b.example" not in response.content.decode()


def test_forbidden_rename_leaves_the_name_alone(people, org_a) -> None:
    client_for(people["accountant"]).patch(
        f"/api/v1/orgs/{org_a.id}", {"name": "Renamed"}, format="json"
    )

    org_a.refresh_from_db()
    assert org_a.name == "Org A"


def test_member_of_both_sees_each_with_its_own_role(people, org_a, org_b) -> None:
    accountant = people["accountant"]
    Membership.objects.create(organization=org_b, user=accountant, role=Role.ANALYST)
    client = client_for(accountant)

    in_a = client.get(f"/api/v1/orgs/{org_a.id}/members/me").json()
    in_b = client.get(f"/api/v1/orgs/{org_b.id}/members/me").json()

    assert (in_a["role"], in_b["role"]) == ("accountant", "analyst")
    assert client.patch(f"/api/v1/orgs/{org_b.id}", {"name": "X"}, format="json").status_code == 403


def test_deactivated_user_loses_access(people, org_a) -> None:
    owner = people["owner"]
    client = client_for(owner)
    owner.is_active = False
    owner.save()

    assert client.get(f"/api/v1/orgs/{org_a.id}").status_code == 401


def test_rename_ignores_slug_and_currency(people, org_a) -> None:
    response = client_for(people["owner"]).patch(
        f"/api/v1/orgs/{org_a.id}",
        {"name": "  New name ", "slug": "taken", "base_currency": "USD"},
        format="json",
    )

    assert response.status_code == 200
    org_a.refresh_from_db()
    assert (org_a.name, org_a.slug, org_a.base_currency) == ("New name", "org-a", "EUR")


def test_blank_name_is_rejected(people, org_a) -> None:
    response = client_for(people["owner"]).patch(
        f"/api/v1/orgs/{org_a.id}", {"name": "   "}, format="json"
    )

    assert response.status_code == 400


def test_member_list_shows_only_own_organization(people, org_a) -> None:
    response = client_for(people["owner"]).get(f"/api/v1/orgs/{org_a.id}/members")

    emails = [m["user"]["email"] for m in response.json()]
    assert emails == ["accountant@a.example", "analyst@a.example", "owner@a.example"]


def test_unlisted_methods_are_denied_even_for_owners(people, org_a) -> None:
    client = client_for(people["owner"])

    assert client.delete(f"/api/v1/orgs/{org_a.id}").status_code == 403
    assert client.put(f"/api/v1/orgs/{org_a.id}", {"name": "X"}, format="json").status_code == 403
