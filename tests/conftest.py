"""Shared pytest fixtures.

Each test session runs against a throwaway SQLite database seeded with the same
synthetic SAMPLE data the app ships with, so tests exercise the real retrieval,
answer-policy, publishing and ticket code paths (no mocks).
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

# --- Environment must be configured BEFORE importing the app ---------------
_TMP = tempfile.mkdtemp(prefix="campusmate-tests-")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TMP}/test.db")
os.environ.setdefault("UPLOAD_DIR", f"{_TMP}/documents")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("CAMPUSMATE_SEED", "1")
os.environ.setdefault("CAMPUSMATE_DATASET", "demo")
os.environ.setdefault("LLM_PROVIDER", "stub")
os.environ.setdefault("EMBEDDING_PROVIDER", "hashing")

# The admin account is provisioned from the environment (no default password is
# committed). Tests supply their own private credentials here.
TEST_ADMIN_EMAIL = "admin@campusmate-tests.edu"
TEST_ADMIN_PASSWORD = "test-admin-password"
os.environ.setdefault("SEED_ADMIN_EMAIL", TEST_ADMIN_EMAIL)
os.environ.setdefault("SEED_ADMIN_PASSWORD", TEST_ADMIN_PASSWORD)

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def admin_token(client) -> str:
    resp = client.post(
        "/auth/login",
        json={
            "email": os.environ["SEED_ADMIN_EMAIL"],
            "password": os.environ["SEED_ADMIN_PASSWORD"],
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(admin_token) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}
