"""Organization-scoped authorization for API views.

Every URL that touches tenant data carries the organization ID
(`/api/v1/orgs/<org_id>/...`). `IsOrganizationMember` resolves the caller's
membership for that organization once per request and then checks the role
against the view's `org_roles` table:

    class InvoiceList(OrganizationScopedView):
        org_roles = {"GET": ALL_ROLES, "POST": {Role.OWNER, Role.ACCOUNTANT}}

Rules:

* Not signed in: 401.
* Not a member (or the organization does not exist): 404, so IDs of other
  tenants cannot be probed.
* Member, but the method is missing from `org_roles` or the role is not
  listed: 403. Methods are denied unless a view opts in.
"""

from collections.abc import Collection, Mapping

from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Membership, Organization, Role

ALL_ROLES: frozenset[str] = frozenset(Role.values)
READ_ONLY_FOR_ALL: Mapping[str, Collection[str]] = {"GET": ALL_ROLES, "HEAD": ALL_ROLES}


def allowed_roles(view: APIView, method: str) -> Collection[str]:
    table: Mapping[str, Collection[str]] = getattr(view, "org_roles", {})
    return table.get(method.upper(), ())


class IsOrganizationMember(BasePermission):
    message = "Your role in this organization does not allow this action."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if user is None or not user.is_authenticated:
            return False  # DRF turns this into 401 via the authenticator's challenge

        org_id = view.kwargs.get("org_id")
        membership = (
            Membership.objects.for_user(user)
            .select_related("organization")
            .filter(organization_id=org_id)
            .first()
        )
        if membership is None:
            raise NotFound()

        request.membership = membership
        return membership.role in allowed_roles(view, request.method)


class OrganizationScopedView(APIView):
    """Base class for views under `/orgs/<org_id>/`."""

    permission_classes = [IsOrganizationMember]
    org_roles: Mapping[str, Collection[str]] = READ_ONLY_FOR_ALL

    @property
    def membership(self) -> Membership:
        return self.request.membership

    @property
    def organization(self) -> Organization:
        return self.request.membership.organization
