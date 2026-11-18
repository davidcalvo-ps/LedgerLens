"""Runtime settings read from the environment once at startup."""

import os
from dataclasses import dataclass

SERVICE_NAME = "ai-api"


@dataclass(frozen=True)
class Settings:
    version: str
    environment: str
    # The AI API is internal; interactive docs are only exposed for local work.
    docs_enabled: bool


def load_settings() -> Settings:
    environment = os.environ.get("LEDGERLENS_ENV", "local")
    return Settings(
        version=os.environ.get("LEDGERLENS_VERSION", "0.1.0"),
        environment=environment,
        docs_enabled=environment == "local",
    )
