"""Session authentication and workspace endpoints.

The web app is served from the same origin as the API (the Vite dev server
proxies `/api`), so a Django session cookie plus CSRF token is the whole auth
story: no tokens are ever stored in browser JavaScript.
"""

from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Membership, Role
from .permissions import READ_ONLY_FOR_ALL, OrganizationScopedView
from .serializers import (
    LoginSerializer,
    MemberSerializer,
    MembershipSerializer,
    OrganizationSerializer,
    OrganizationUpdateSerializer,
    UserSerializer,
)

INVALID_CREDENTIALS = "Invalid email or password."


def session_payload(user) -> dict:
    memberships = Membership.objects.for_user(user).select_related("organization")
    return {
        "user": UserSerializer(user).data,
        "memberships": MembershipSerializer(memberships, many=True).data,
    }


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    """Sets the CSRF cookie so the SPA can send the token on its first POST."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    # DRF only enforces CSRF for already-authenticated sessions; login is
    # protected explicitly so a third-party site cannot sign a browser in.
    authentication_classes: list = []
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request._request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            # Same answer for unknown email, wrong password and inactive user.
            return Response({"detail": INVALID_CREDENTIALS}, status=status.HTTP_400_BAD_REQUEST)
        login(request._request, user)  # rotates the session key and CSRF token
        return Response(session_payload(user))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        logout(request._request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionView(APIView):
    """The signed-in user and every organization they belong to."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(session_payload(request.user))


class CurrentMemberView(OrganizationScopedView):
    """The caller's membership in one organization (any role)."""

    def get(self, request: Request, org_id) -> Response:
        return Response(MembershipSerializer(self.membership).data)


class OrganizationDetailView(OrganizationScopedView):
    """Workspace details: every member reads, only owners rename."""

    org_roles = {**READ_ONLY_FOR_ALL, "PATCH": {Role.OWNER}}

    def get(self, request: Request, org_id) -> Response:
        return Response(OrganizationSerializer(self.organization).data)

    def patch(self, request: Request, org_id) -> Response:
        serializer = OrganizationUpdateSerializer(
            self.organization, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrganizationSerializer(serializer.instance).data)


class MemberListView(OrganizationScopedView):
    """Who belongs to the workspace and with which role (owners only)."""

    org_roles = {"GET": {Role.OWNER}, "HEAD": {Role.OWNER}}

    def get(self, request: Request, org_id) -> Response:
        members = (
            Membership.objects.filter(organization=self.organization, user__is_active=True)
            .select_related("user")
            .order_by("user__email")
        )
        return Response(MemberSerializer(members, many=True).data)
