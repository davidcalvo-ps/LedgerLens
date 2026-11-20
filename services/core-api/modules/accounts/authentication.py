"""Session authentication that answers 401 when nobody is signed in.

DRF's stock SessionAuthentication sends no WWW-Authenticate header, so a
missing or expired session comes back as 403, the same status as "signed in
but not allowed". The web app needs to tell the two apart to send people back
to the sign-in page, so this class names a challenge and DRF switches the
unauthenticated case to 401.
"""

from rest_framework.authentication import SessionAuthentication as DrfSessionAuthentication
from rest_framework.request import Request


class SessionAuthentication(DrfSessionAuthentication):
    def authenticate_header(self, request: Request) -> str:
        return 'Session realm="ledgerlens"'
