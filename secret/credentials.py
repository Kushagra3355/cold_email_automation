"""
secret/credentials.py
---------------------
Loads your email + app password WITHOUT hardcoding them in the script.

Priority:
  1. Environment variables  (EMAIL_SENDER, EMAIL_APP_PASSWORD)
  2. A local secret/.env file (key=value lines) - gitignored
  3. Interactive prompt (password hidden as you type)

The app password is never printed or written back to disk by this module.
"""

import os
import getpass
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"


def _load_env_file():
    """Read simple KEY=VALUE lines from secret/.env if it exists."""
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def get_credentials():
    """Return (sender_email, app_password) from env -> .env -> prompt."""
    file_vals = _load_env_file()

    sender = (
        os.environ.get("EMAIL_SENDER")
        or file_vals.get("EMAIL_SENDER")
    )
    password = (
        os.environ.get("EMAIL_APP_PASSWORD")
        or file_vals.get("EMAIL_APP_PASSWORD")
    )

    if not sender:
        sender = input("Sender email: ").strip()
    if not password:
        # getpass hides the input so it never shows on screen
        password = getpass.getpass("App password (hidden): ").strip()

    return sender, password
