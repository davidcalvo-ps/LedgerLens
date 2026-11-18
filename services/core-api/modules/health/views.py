from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import checks


class PublicHealthView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]


class LivenessView(PublicHealthView):
    """The process is up and serving requests. No dependencies are touched."""

    def get(self, request: Request) -> Response:
        return Response(
            {
                "status": "ok",
                "service": settings.SERVICE_NAME,
                "version": settings.SERVICE_VERSION,
            }
        )


class ReadinessView(PublicHealthView):
    """The service can reach PostgreSQL and Redis. Returns 503 otherwise."""

    def get(self, request: Request) -> Response:
        results = {name: probe() for name, probe in checks.PROBES.items()}
        ready = all(results.values())
        return Response(
            {
                "status": "ok" if ready else "unavailable",
                "service": settings.SERVICE_NAME,
                "version": settings.SERVICE_VERSION,
                "checks": {name: "ok" if ok else "failing" for name, ok in results.items()},
            },
            status=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
