"""Settings for the unit test suite: no external services required."""

from .base import *  # noqa: F403

SECRET_KEY = "test-only-not-secret"
DEBUG = False
ALLOWED_HOSTS = ["testserver"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

REDIS_URL = "redis://127.0.0.1:6399/0"
