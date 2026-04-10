"""
keyring_store.py - Read API Keys from OS Keyring
==================================================

This module reads Ambient Weather API keys from the OS credential store.
It provides a single function, get_keys(), that returns the keys.

LOOKUP ORDER:
1. Environment variables (for Docker and CI where keyring isn't available)
2. OS keyring (macOS Keychain, Windows Credential Manager, Linux SecretService)

This means:
- In Docker: keys come from -e flags (environment variables)
- In Claude Desktop: keys come from the env block in config JSON
- In local development: keys come from the OS keyring (set via setup_keys.py)
- Fallback: .env file loaded by python-dotenv (if still present)

The environment variable check comes first so that Docker, CI, and
Claude Desktop configs continue to work without any changes.
"""

import os
import logging

logger = logging.getLogger(__name__)

SERVICE_NAME = "ambient-weather-mcp"


def get_keys() -> dict[str, str]:
    """Retrieve API keys from environment variables or OS keyring.

    Returns:
        A dict with 'api_key' and 'app_key' values.
        Values may be empty strings if not found in either source.
    """
    api_key = os.getenv("AMBIENT_API_KEY", "")
    app_key = os.getenv("AMBIENT_APP_KEY", "")

    # If both are set via environment, use them (Docker, CI, Claude Desktop)
    if api_key and app_key:
        logger.info("API keys loaded from environment variables")
        return {"api_key": api_key, "app_key": app_key}

    # Otherwise, try the OS keyring
    try:
        import keyring

        if not api_key:
            api_key = keyring.get_password(SERVICE_NAME, "AMBIENT_API_KEY") or ""
            if api_key:
                logger.info("AMBIENT_API_KEY loaded from OS keyring")

        if not app_key:
            app_key = keyring.get_password(SERVICE_NAME, "AMBIENT_APP_KEY") or ""
            if app_key:
                logger.info("AMBIENT_APP_KEY loaded from OS keyring")

    except ImportError:
        logger.debug("keyring package not available, skipping keyring lookup")
    except Exception as e:
        logger.warning("Failed to read from OS keyring: %s", e)

    if not api_key:
        logger.warning(
            "AMBIENT_API_KEY not found in environment or keyring. "
            "Run: uv run python -m src.setup_keys"
        )
    if not app_key:
        logger.warning(
            "AMBIENT_APP_KEY not found in environment or keyring. "
            "Run: uv run python -m src.setup_keys"
        )

    return {"api_key": api_key, "app_key": app_key}
