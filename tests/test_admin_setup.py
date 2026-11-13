"""Local admin setup keeps other configuration and round-trips special characters."""
from dotenv import dotenv_values
import pytest
from pydantic import ValidationError

from scripts.setup_admin import write_admin_settings
from scripts.setup_admin import main


def test_setup_preserves_existing_database_and_private_settings(tmp_path):
    env = tmp_path / '.env'
    env.write_text('DATABASE_URL=sqlite:///existing.db\nSECRET_KEY=existing-secret\n')
    password = "Unit-test-only-$#'password-123"
    write_admin_settings(env, 'Local.Admin@example.com', password, 'Local Administrator')
    saved = dotenv_values(env)
    assert saved['DATABASE_URL'] == 'sqlite:///existing.db'
    assert saved['SECRET_KEY'] == 'existing-secret'
    assert saved['SEED_ADMIN_EMAIL'] == 'local.admin@example.com'
    assert saved['SEED_ADMIN_PASSWORD'] == password
    assert saved['SEED_ADMIN_NAME'] == 'Local Administrator'


@pytest.mark.parametrize('email,password', [
    ('not-an-email', 'Long-test-password-123'),
    ('local@example.com', 'short'),
    ('local@example.com', '\u00e9' * 37),
])
def test_invalid_admin_settings_do_not_change_the_file(tmp_path, email, password):
    env = tmp_path / '.env'
    original = 'DATABASE_URL=sqlite:///unchanged.db\n'
    env.write_text(original)
    with pytest.raises((ValueError, ValidationError)):
        write_admin_settings(env, email, password, '')
    assert env.read_text() == original


def test_visible_setup_retries_invalid_password_instead_of_stopping(tmp_path, monkeypatch, capsys):
    env = tmp_path / '.env'
    answers = iter(['Test Admin', 'local@example.com', 'short', 'short',
                    'Test Admin', 'local@example.com', 'Valid-unit-password-123', 'Valid-unit-password-123'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(answers))
    assert main(['--show-password'], env_file=env) == 0
    assert dotenv_values(env)['SEED_ADMIN_EMAIL'] == 'local@example.com'
    output = capsys.readouterr().out
    assert 'WILL BE VISIBLE' in output
    assert 'Try again' in output


def test_hidden_setup_explains_input_and_keeps_password_out_of_output(tmp_path, monkeypatch, capsys):
    answers = iter(['Test Admin', 'local@example.com'])
    password = 'Private-unit-test-password'
    monkeypatch.setattr('builtins.input', lambda prompt: next(answers))
    monkeypatch.setattr('scripts.setup_admin.getpass', lambda prompt: password)
    assert main([], env_file=tmp_path / '.env') == 0
    output = capsys.readouterr().out
    assert 'no characters or stars appear' in output
    assert password not in output
