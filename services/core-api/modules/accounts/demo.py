"""Synthetic demo tenants used for local development and walkthroughs.

All names and addresses are fictional; `.example` is a reserved domain.
The accountant belongs to both organizations, which is what makes the
cross-tenant tests and the workspace switcher meaningful.
"""

from dataclasses import dataclass

from .models import Role


@dataclass(frozen=True)
class DemoOrganization:
    slug: str
    name: str
    base_currency: str


@dataclass(frozen=True)
class DemoMember:
    email: str
    first_name: str
    last_name: str
    memberships: tuple[tuple[str, Role], ...]


ORGANIZATIONS = (
    DemoOrganization(slug="lumen-studio", name="Lumen Design Studio", base_currency="EUR"),
    DemoOrganization(slug="harbor-bakery", name="Harbor Street Bakery", base_currency="EUR"),
)

MEMBERS = (
    DemoMember("lucia@lumen.example", "Lucía", "Demo", (("lumen-studio", Role.OWNER),)),
    DemoMember("sara@lumen.example", "Sara", "Demo", (("lumen-studio", Role.ANALYST),)),
    DemoMember("tomas@harbor.example", "Tomás", "Demo", (("harbor-bakery", Role.OWNER),)),
    DemoMember(
        "martin@books.example",
        "Martín",
        "Demo",
        (("lumen-studio", Role.ACCOUNTANT), ("harbor-bakery", Role.ACCOUNTANT)),
    ),
)
