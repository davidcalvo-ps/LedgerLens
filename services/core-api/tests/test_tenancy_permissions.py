"""Cross-tenant isolation and the role matrix for organization-scoped APIs.

Uses the shared permission fixtures in `conftest.py`: two organizations, one
person per role in A, plus an outsider who only belongs to B. Every scoped
endpoint is exercised with every caller.
"""

import pytest
from rest_framework.test import APIClient

from modules.accounts.models import Membership, Role

pytestmark = pytest.mark.django_db


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
    for role in Role.values
]


@pytest.mark.parametrize(("method", "path", "payload", "role", "expected"), CASES)
def test_role_matrix(as_user, people, org_a, method, path, payload, role, expected) -> None:
    client = as_user(people[role])

    response = getattr(client, method)(path.format(org=org_a.id), payload, format="json")

    assert response.status_code == expected


@pytest.mark.parametrize(("method", "path", "payload", "_role", "_expected"), CASES[::3])
def test_outsider_gets_404_for_every_endpoint(
    as_user, people, org_a, method, path, payload, _role, _expected
) -> None:
    client = as_user(people["outsider"])

    response = getattr(client, method)(path.format(org=org_a.id), payload, format="json")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found."}


@pytest.mark.parametrize(("method", "path", "payload", "_role", "_expected"), CASES[::3])
def test_anonymous_gets_401_for_every_endpoint(
    org_a, method, path, payload, _role, _expected
) -> None:
    response = getattr(APIClient(), method)(path.format(org=org_a.id), payload, format="json")

    assert response.status_code == 401


def test_owner_of_a_cannot_rename_b(as_user, people, org_b) -> None:
    client = as_user(people["owner"])

    response = client.patch(f"/api/v1/orgs/{org_b.id}", {"name": "Hijacked"}, format="json")

    assert response.status_code == 404
    org_b.refresh_from_db()
    assert org_b.name == "Org B"


def test_owner_of_a_cannot_list_b_members(as_user, people, org_b) -> None:
    response = as_user(people["owner"]).get(f"/api/v1/orgs/{org_b.id}/members")

    assert response.status_code == 404
    assert "owner@b.example" not in response.content.decode()


def test_forbidden_rename_leaves_the_name_alone(as_user, people, org_a) -> None:
    as_user(people["accountant"]).patch(
        f"/api/v1/orgs/{org_a.id}", {"name": "Renamed"}, format="json"
    )

    org_a.refresh_from_db()
    assert org_a.name == "Org A"


def test_member_of_both_sees_each_with_its_own_role(as_user, people, org_a, org_b) -> None:
    accountant = people["accountant"]
    Membership.objects.create(organization=org_b, user=accountant, role=Role.ANALYST)
    client = as_user(accountant)

    in_a = client.get(f"/api/v1/orgs/{org_a.id}/members/me").json()
    in_b = client.get(f"/api/v1/orgs/{org_b.id}/members/me").json()

    assert (in_a["role"], in_b["role"]) == ("accountant", "analyst")
    assert client.patch(f"/api/v1/orgs/{org_b.id}", {"name": "X"}, format="json").status_code == 403


def test_deactivated_user_loses_access(as_user, people, org_a) -> None:
    owner = people["owner"]
    client = as_user(owner)
    owner.is_active = False
    owner.save()

    assert client.get(f"/api/v1/orgs/{org_a.id}").status_code == 401


def test_rename_ignores_slug_and_currency(as_user, people, org_a) -> None:
    response = as_user(people["owner"]).patch(
        f"/api/v1/orgs/{org_a.id}",
        {"name": "  New name ", "slug": "taken", "base_currency": "USD"},
        format="json",
    )

    assert response.status_code == 200
    org_a.refresh_from_db()
    assert (org_a.name, org_a.slug, org_a.base_currency) == ("New name", "org-a", "EUR")


def test_blank_name_is_rejected(as_user, people, org_a) -> None:
    response = as_user(people["owner"]).patch(
        f"/api/v1/orgs/{org_a.id}", {"name": "   "}, format="json"
    )

    assert response.status_code == 400


def test_member_list_shows_only_own_organization(as_user, people, org_a) -> None:
    response = as_user(people["owner"]).get(f"/api/v1/orgs/{org_a.id}/members")

    emails = [m["user"]["email"] for m in response.json()]
    assert emails == ["accountant@a.example", "analyst@a.example", "owner@a.example"]


def test_unlisted_methods_are_denied_even_for_owners(as_user, people, org_a) -> None:
    client = as_user(people["owner"])

    assert client.delete(f"/api/v1/orgs/{org_a.id}").status_code == 403
    assert client.put(f"/api/v1/orgs/{org_a.id}", {"name": "X"}, format="json").status_code == 403
