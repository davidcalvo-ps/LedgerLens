"""Dependency probes used by the readiness endpoint.

Each probe returns True or False and never raises: failure details are logged on
the server, not returned to the caller.
"""

import logging

import redis
from django.conf import settings
from django.db import connection

logger = logging.getLogger(__name__)

PROBE_TIMEOUT_SECONDS = 2


def database_ok() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        logger.warning("Database health check failed", exc_info=True)
        return False
    return True


def redis_ok() -> bool:
    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=PROBE_TIMEOUT_SECONDS,
            socket_timeout=PROBE_TIMEOUT_SECONDS,
        )
        try:
            return bool(client.ping())
        finally:
            client.close()
    except Exception:
        logger.warning("Redis health check failed", exc_info=True)
        return False


PROBES = {
    "database": database_ok,
    "redis": redis_ok,
}
