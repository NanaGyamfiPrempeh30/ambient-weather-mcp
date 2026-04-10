"""
setup_keys.py - Store API Keys in OS Keyring
==============================================

This script stores your Ambient Weather API keys in your operating
system's secure credential store:
  - macOS: Keychain
  - Windows: Credential Manager
  - Linux: SecretService (GNOME Keyring / KDE Wallet)

Keys are stored securely by the OS, encrypted at rest, and never
written to a plain-text file on disk.

USAGE:
  uv run python -m src.setup_keys

  The script prompts you for each key interactively.
  Run it once per machine. Keys persist across reboots.

TO VIEW STORED KEYS (for debugging):
  uv run python -c "from src.keyring_store import get_keys; print(get_keys())"

TO DELETE STORED KEYS:
  uv run python -m src.setup_keys --delete
"""

import sys
import argparse
import keyring

# Service name used to identify our keys in the OS keyring.
# All our keys are stored under this service name.
SERVICE_NAME = "ambient-weather-mcp"

# The two keys we need to store
KEY_NAMES = ["AMBIENT_API_KEY", "AMBIENT_APP_KEY"]


def store_keys():
    """Prompt the user for API keys and store them in the OS keyring."""
    print("Ambient Weather MCP Server — Key Setup")
    print("=" * 40)
    print()
    print("This stores your API keys in your OS credential manager.")
    print("Keys are encrypted at rest and never written to a file.")
    print()
    print("Get your keys at: https://dashboard.ambientweather.net/account")
    print()

    for key_name in KEY_NAMES:
        # Check if a key already exists
        existing = keyring.get_password(SERVICE_NAME, key_name)
        if existing:
            print(f"{key_name}: already stored (starts with {existing[:8]}...)")
            overwrite = input("  Overwrite? (y/N): ").strip().lower()
            if overwrite != "y":
                print("  Skipped.")
                continue

        value = input(f"Enter {key_name}: ").strip()
        if not value:
            print("  Empty value, skipping.")
            continue

        keyring.set_password(SERVICE_NAME, key_name, value)
        print(f"  Stored successfully.")

    print()
    print("Done. Your keys are now stored in the OS credential manager.")
    print("The MCP server will read them automatically on startup.")


def delete_keys():
    """Remove stored keys from the OS keyring."""
    print("Deleting stored API keys...")
    for key_name in KEY_NAMES:
        try:
            keyring.delete_password(SERVICE_NAME, key_name)
            print(f"  {key_name}: deleted.")
        except keyring.errors.PasswordDeleteError:
            print(f"  {key_name}: not found (already deleted).")
    print("Done.")


def main():
    parser = argparse.ArgumentParser(
        description="Store Ambient Weather API keys in OS keyring"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete stored keys instead of setting them",
    )
    args = parser.parse_args()

    if args.delete:
        delete_keys()
    else:
        store_keys()


if __name__ == "__main__":
    main()
