"""Set up the administrator once inside the main Run command."""
from __future__ import annotations

from pathlib import Path
import os
import sys

from dotenv import dotenv_values

try:
    from .setup_admin import main as setup_admin
except ImportError:
    from setup_admin import main as setup_admin


def admin_configured(env_file: Path, environ=None) -> bool:
    environ = os.environ if environ is None else environ
    config = dotenv_values(env_file) if env_file.exists() else {}
    email = environ.get('SEED_ADMIN_EMAIL',config.get('SEED_ADMIN_EMAIL')) or ''
    password = environ.get('SEED_ADMIN_PASSWORD',config.get('SEED_ADMIN_PASSWORD')) or ''
    return bool(email.strip() and password)


def main(argv: list[str] | None = None, *, env_file: Path | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    env_file = env_file or Path(__file__).resolve().parents[1] / 'backend/.env'
    if admin_configured(env_file) and '--reset-admin' not in argv:
        print('Administrator settings are ready.')
        return 0
    print('First launch: choose your administrator login once.')
    print('This local setup shows password characters as you type.')
    result = setup_admin(['--show-password'],env_file=env_file)
    if result == 0:
        print('Admin login saved. Continuing automatically to start CampusMate.')
    return result


if __name__ == '__main__':
    raise SystemExit(main())
