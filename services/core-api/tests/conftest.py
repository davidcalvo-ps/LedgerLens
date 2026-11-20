"""Shared permission fixtures.

The tenancy layout every authorization test starts from:

* `org_a` with one member per role (`people["owner"]`, `people["accountant"]`,
  `people["analyst"]`), all at `<role>@a.example`;
* `org_b` owned by `people["outsider"]`, who has no membership in `org_a`.

Later modules (ledger, imports, invoices) reuse these fixtures so every new
organization-scoped endpoint is tested against the same callers.
"""

from collections.abc import Callable

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from modules.accounts.models import Membership, Organization, Role


def make_user(email: str, **extra):
    """An active user with an unusable password (tests sign in with force_login)."""
    return get_user_model().objects.create_user(
        username=email, email=email, password=None, **extra
    )


@pytest.fixture
def org_a(db) -> Organization:
    return Organization.objects.create(name="Org A", slug="org-a")


@pytest.fixture
def org_b(db) -> Organization:
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


@pytest.fixture
def as_user() -> Callable[..., APIClient]:
    """Factory: `as_user(people["owner"])` returns a client signed in as that user."""

    def build(user) -> APIClient:
        client = APIClient()
        client.force_login(user)
        return client

    return build
