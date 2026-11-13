"""Choose local administrator credentials without putting them in the UI or code."""
from __future__ import annotations

from getpass import getpass
from pathlib import Path
import argparse
import os

from dotenv import set_key
from pydantic import EmailStr, TypeAdapter, ValidationError


def write_admin_settings(env_file: Path, email: str, password: str, name: str) -> None:
    email = str(TypeAdapter(EmailStr).validate_python(email.strip())).lower()
    if len(password) < 12 or len(password.encode('utf-8')) > 72:
        raise ValueError('Use a password of at least 12 characters and at most 72 UTF-8 bytes.')
    if '\n' in password or '\r' in password:
        raise ValueError('The password must be on one line.')
    name = name.strip() or 'CampusMate Administrator'
    if len(name) > 255:
        raise ValueError('The administrator name is too long.')
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.touch(exist_ok=True)
    for key, value in {
        'SEED_ADMIN_EMAIL': email,
        'SEED_ADMIN_PASSWORD': password,
        'SEED_ADMIN_NAME': name,
    }.items():
        set_key(str(env_file), key, value, quote_mode='always')
    if os.name != 'nt':
        env_file.chmod(0o600)


def main(argv: list[str] | None = None, *, env_file: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--show-password', action='store_true', help='Show password characters while typing locally.')
    args = parser.parse_args(argv)
    env_file = env_file or Path(__file__).resolve().parents[1] / 'backend/.env'
    print('CampusMate — set up your local admin login')
    if args.show_password:
        print('Password characters WILL BE VISIBLE on this computer while typing.')
    else:
        print('The password field is hidden: no characters or stars appear. Type normally and press Enter.')
    password_input = input if args.show_password else getpass
    while True:
        try:
            name = input('Admin display name (Enter for default): ')
            email = input('Admin email: ')
            password = password_input('Admin password (at least 12 characters): ')
            if password_input('Confirm password: ') != password:
                print('Passwords do not match. Nothing was changed. Try again.')
                continue
            write_admin_settings(env_file, email, password, name)
            break
        except (ValidationError, ValueError):
            # Validation errors may contain their input; do not echo credentials.
            print('Nothing was changed. Use a valid email and a password of at least 12 characters (maximum 72 UTF-8 bytes). Try again.')
        except (EOFError, KeyboardInterrupt):
            print('\nSetup cancelled. No admin settings were changed.')
            return 1
    print('Admin settings saved. Restart the backend, then click Admin Login.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
