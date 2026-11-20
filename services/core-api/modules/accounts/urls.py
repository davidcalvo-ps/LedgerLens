from django.urls import path

from .views import (
    CsrfView,
    CurrentMemberView,
    LoginView,
    LogoutView,
    MemberListView,
    OrganizationDetailView,
    SessionView,
)

app_name = "accounts"

urlpatterns = [
    path("auth/csrf", CsrfView.as_view(), name="csrf"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("auth/session", SessionView.as_view(), name="session"),
    path("orgs/<uuid:org_id>", OrganizationDetailView.as_view(), name="organization"),
    path("orgs/<uuid:org_id>/members", MemberListView.as_view(), name="members"),
    path("orgs/<uuid:org_id>/members/me", CurrentMemberView.as_view(), name="current-member"),
]
