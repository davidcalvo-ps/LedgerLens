import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction

from modules.accounts.models import Membership, Organization, Role

pytestmark = pytest.mark.django_db

DEMO_PASSWORD = "harbor-lumen-demo-2026"


def make_user(email: str):
    return get_user_model().objects.create_user(username=email, email=email, password="x")


def test_a_user_belongs_to_an_organization_once() -> None:
    org = Organization.objects.create(name="Acme", slug="acme")
    user = make_user("a@acme.example")
    Membership.objects.create(organization=org, user=user, role=Role.OWNER)

    with pytest.raises(IntegrityError), transaction.atomic():
        Membership.objects.create(organization=org, user=user, role=Role.ANALYST)


def test_unknown_roles_are_rejected_by_the_database() -> None:
    org = Organization.objects.create(name="Acme", slug="acme")
    user = make_user("a@acme.example")

    with pytest.raises(IntegrityError), transaction.atomic():
        Membership.objects.create(organization=org, user=user, role="admin")


def test_base_currency_must_be_an_iso_code() -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Organization.objects.create(name="Acme", slug="acme", base_currency="eur")


def test_for_user_ignores_anonymous_and_inactive_users() -> None:
    org = Organization.objects.create(name="Acme", slug="acme")
    user = make_user("a@acme.example")
    Membership.objects.create(organization=org, user=user, role=Role.OWNER)

    assert Membership.objects.for_user(None).count() == 0
    assert Membership.objects.for_user(user).count() == 1
    user.is_active = False
    user.save()
    assert Membership.objects.for_user(user).count() == 0


def test_seed_creates_two_organizations_and_is_idempotent(settings) -> None:
    settings.DEBUG = True
    call_command("seed_demo_orgs", password=DEMO_PASSWORD)
    call_command("seed_demo_orgs", password=DEMO_PASSWORD)

    assert sorted(Organization.objects.values_list("slug", flat=True)) == [
        "harbor-bakery",
        "lumen-studio",
    ]
    assert get_user_model().objects.count() == 4
    assert Membership.objects.count() == 5
    accountant = Membership.objects.filter(user__email="martin@books.example")
    assert set(accountant.values_list("role", flat=True)) == {Role.ACCOUNTANT}
    assert accountant.count() == 2


def test_seed_refuses_to_run_without_debug(settings) -> None:
    settings.DEBUG = False
    with pytest.raises(CommandError, match="DEBUG"):
        call_command("seed_demo_orgs", password=DEMO_PASSWORD)
    assert Organization.objects.count() == 0


def test_seed_rejects_weak_or_missing_passwords(settings, monkeypatch) -> None:
    settings.DEBUG = True
    monkeypatch.delenv("LEDGERLENS_DEMO_PASSWORD", raising=False)
    with pytest.raises(CommandError, match="LEDGERLENS_DEMO_PASSWORD"):
        call_command("seed_demo_orgs")
    with pytest.raises(CommandError):
        call_command("seed_demo_orgs", password="short")
