"""Tenancy: organizations and the people who belong to them.

Every business record created in later modules belongs to exactly one
organization. A user sees an organization only through a membership, and the
membership's role decides what they may do there.
"""

import uuid

from django.conf import settings
from django.db import models


class Role(models.TextChoices):
    OWNER = "owner", "Owner"
    ACCOUNTANT = "accountant", "Accountant"
    ANALYST = "analyst", "Analyst"


class Organization(models.Model):
    # Random public identifiers so organization IDs cannot be enumerated.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=60, unique=True)
    base_currency = models.CharField(max_length=3, default="EUR")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "organizations"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base_currency__regex=r"^[A-Z]{3}$"),
                name="organization_currency_iso_4217",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class MembershipQuerySet(models.QuerySet):
    def for_user(self, user) -> "MembershipQuerySet":
        if user is None or not user.is_authenticated:
            return self.none()
        return self.filter(user=user, user__is_active=True)


class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MembershipQuerySet.as_manager()

    class Meta:
        db_table = "memberships"
        ordering = ["organization__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"], name="membership_unique_user_per_org"
            ),
            models.CheckConstraint(
                condition=models.Q(role__in=Role.values), name="membership_role_valid"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.organization} ({self.role})"
