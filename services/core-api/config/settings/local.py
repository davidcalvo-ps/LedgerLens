"""Settings for local development, including the Compose stack."""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import SECRET_KEY

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"

if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set (copy .env.example to .env).")

# Local development runs over plain HTTP.
SECURE_COOKIES = env_bool("DJANGO_SECURE_COOKIES", False)  # noqa: F405
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES
