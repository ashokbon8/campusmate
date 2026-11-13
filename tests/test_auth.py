"""Authentication and authorisation."""

import os

import pytest

ADMIN_EMAIL = os.environ["SEED_ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["SEED_ADMIN_PASSWORD"]


def test_login_with_valid_credentials(client):
    resp = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_with_bad_password_is_rejected(client):
    resp = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": "wrong"},
    )
    assert resp.status_code == 401


def test_me_requires_authentication(client):
    assert client.get("/auth/me").status_code == 401


def test_me_returns_current_admin(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == ADMIN_EMAIL
    assert resp.json()["role"] == "admin"


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/admin/notices"),
        ("get", "/admin/overview"),
        ("get", "/admin/tickets"),
    ],
)
def test_admin_endpoints_require_auth(client, method, path):
    assert getattr(client, method)(path).status_code == 401


def test_upload_requires_publisher_role(client):
    # No auth at all -> 401 (never a 200).
    files = {"file": ("x.pdf", b"%PDF-1.4", "application/pdf")}
    resp = client.post(
        "/admin/notices",
        data={"title": "x", "category": "Fees", "doc_type": "pdf"},
        files=files,
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Student accounts (public sign-up / sign-in)
# ---------------------------------------------------------------------------
STUDENT = {
    "full_name": "Asha Rao",
    "email": "asha.student@example.com",
    "password": "correct-horse-battery",
    "programme": "BSc CS",
    "semester": "1",
}


def test_student_signup_creates_account_and_returns_token(client):
    resp = client.post("/auth/student/signup", json=STUDENT)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["access_token"]
    assert data["account"]["email"] == STUDENT["email"]
    assert data["account"]["full_name"] == STUDENT["full_name"]
    # The password (or its hash) must never come back in the response.
    assert "password" not in data["account"]
    assert "hashed_password" not in data["account"]


def test_student_signup_rejects_duplicate_email(client):
    assert client.post("/auth/student/signup", json=STUDENT).status_code == 409


def test_student_signup_rejects_short_password(client):
    resp = client.post(
        "/auth/student/signup",
        json={**STUDENT, "email": "short@example.com", "password": "short"},
    )
    assert resp.status_code == 422


def test_student_login_and_me(client):
    resp = client.post(
        "/auth/student/login",
        json={"email": STUDENT["email"], "password": STUDENT["password"]},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me = client.get("/auth/student/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == STUDENT["email"]


def test_student_login_rejects_wrong_password(client):
    resp = client.post(
        "/auth/student/login",
        json={"email": STUDENT["email"], "password": "not-the-password"},
    )
    assert resp.status_code == 401


def test_student_me_requires_authentication(client):
    assert client.get("/auth/student/me").status_code == 401


def test_student_token_cannot_reach_admin_endpoints(client):
    token = client.post(
        "/auth/student/login",
        json={"email": STUDENT["email"], "password": STUDENT["password"]},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/auth/me", headers=headers).status_code == 401
    assert client.get("/admin/overview", headers=headers).status_code == 401


def test_admin_token_cannot_be_used_as_student(client, auth_headers):
    assert client.get("/auth/student/me", headers=auth_headers).status_code == 401


def test_student_with_same_email_as_admin_does_not_gain_admin_access(client, auth_headers):
    import os
    response = client.post('/auth/student/signup', json={
        'full_name': 'Student with a shared email',
        'email': os.environ['SEED_ADMIN_EMAIL'],
        'password': 'student-test-password-only',
    })
    assert response.status_code == 201
    student_headers = {'Authorization': f"Bearer {response.json()['access_token']}"}
    assert client.get('/auth/student/me', headers=student_headers).status_code == 200
    assert client.get('/auth/me', headers=student_headers).status_code == 401
    assert client.get('/admin/overview', headers=student_headers).status_code == 401
    assert client.get('/auth/student/me', headers=auth_headers).status_code == 401
    assert client.get('/auth/me', headers=auth_headers).status_code == 200


def test_admin_email_is_case_insensitive(client):
    import os
    response = client.post('/auth/login', json={
        'email': os.environ['SEED_ADMIN_EMAIL'].upper(),
        'password': os.environ['SEED_ADMIN_PASSWORD'],
    })
    assert response.status_code == 200
