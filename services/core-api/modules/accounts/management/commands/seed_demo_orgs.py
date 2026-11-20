"""Create the two demo organizations and their members.

Safe to run repeatedly: existing rows are updated in place, never duplicated.
Refuses to run unless DEBUG is on, so it cannot plant known passwords in a
shared environment by accident.
"""

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from modules.accounts.demo import MEMBERS, ORGANIZATIONS
from modules.accounts.models import Membership, Organization

PASSWORD_ENV = "LEDGERLENS_DEMO_PASSWORD"


class Command(BaseCommand):
    help = "Seed the Lumen Design Studio and Harbor Street Bakery demo organizations."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--password",
            help=f"Password for every demo user (default: ${PASSWORD_ENV}).",
        )

    def handle(self, *args, **options) -> None:
        if not settings.DEBUG:
            raise CommandError("Demo data is only seeded when DEBUG is on.")

        password = options["password"] or os.environ.get(PASSWORD_ENV, "")
        if not password:
            raise CommandError(f"Pass --password or set {PASSWORD_ENV}.")
        try:
            validate_password(password)
        except ValidationError as error:
            raise CommandError(" ".join(error.messages)) from error

        with transaction.atomic():
            orgs = {}
            for demo in ORGANIZATIONS:
                org, _ = Organization.objects.update_or_create(
                    slug=demo.slug,
                    defaults={"name": demo.name, "base_currency": demo.base_currency},
                )
                orgs[demo.slug] = org

            User = get_user_model()
            for demo in MEMBERS:
                user, _ = User.objects.update_or_create(
                    username=demo.email,
                    defaults={
                        "email": demo.email,
                        "first_name": demo.first_name,
                        "last_name": demo.last_name,
                        "is_active": True,
                    },
                )
                user.set_password(password)
                user.save(update_fields=["password"])
                for slug, role in demo.memberships:
                    Membership.objects.update_or_create(
                        organization=orgs[slug], user=user, defaults={"role": role}
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(ORGANIZATIONS)} organizations and {len(MEMBERS)} demo users."
            )
        )
        for demo in MEMBERS:
            roles = ", ".join(f"{role.value} @ {slug}" for slug, role in demo.memberships)
            self.stdout.write(f"  {demo.email}: {roles}")
