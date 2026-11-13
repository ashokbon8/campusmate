from pathlib import Path
from types import SimpleNamespace

import pytest


def upload_pdf(client, auth_headers):
    from app.services.pdf_writer import build_pdf
    original = build_pdf(["[SAMPLE] Cloud source preservation", "Original uploaded PDF stays available after restart."])
    response = client.post(
        "/admin/notices", headers=auth_headers,
        data={"title": "Cloud source preservation (sample)", "category": "College activities", "doc_type": "pdf"},
        files={"file": ("original.pdf", original, "application/pdf")},
    )
    assert response.status_code == 201, response.text
    doc = response.json()
    from app.database import SessionLocal
    from app.models import Document
    with SessionLocal() as db:
        Path(db.get(Document, doc["id"]).stored_path).unlink()
    return doc, original


def test_original_pdf_survives_loss_of_cloud_local_storage(client, auth_headers):
    doc, original = upload_pdf(client, auth_headers)
    assert client.get(f"/documents/{doc['doc_uid']}/source").status_code == 404
    published = client.post(f"/admin/notices/{doc['id']}/publish", headers=auth_headers)
    assert published.status_code == 200, published.text
    source = client.get(f"/documents/{doc['doc_uid']}/source")
    assert source.status_code == 200
    assert source.content == original


def test_pdf_can_be_reindexed_after_cloud_local_storage_is_lost(client, auth_headers):
    doc, _ = upload_pdf(client, auth_headers)
    response = client.post(f"/admin/notices/{doc['id']}/reindex", headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json()["passages_indexed"] >= 1


@pytest.mark.parametrize("overrides,message", [
    ({"database_url": "sqlite:///temporary.db"}, "persistent PostgreSQL"),
    ({"secret_key": "change-me-in-production"}, "SECRET_KEY"),
    ({"seed_admin_password": ""}, "SEED_ADMIN_EMAIL"),
])
def test_cloud_launch_rejects_missing_persistence_and_private_settings(monkeypatch, overrides, message):
    from app import cloud
    values = dict(database_url="postgresql://test@db/campusmate", secret_key="s"*48,
                  seed_admin_email="test@example.com", seed_admin_password="test-admin-private")
    values.update(overrides)
    monkeypatch.setattr(cloud, "settings", SimpleNamespace(**values))
    with pytest.raises(RuntimeError, match=message):
        cloud.create_cloud_app()


def test_cloud_entrypoint_uses_combined_app(monkeypatch):
    from app import cloud
    monkeypatch.setattr(cloud, "settings", SimpleNamespace(
        database_url="postgresql://test@db/campusmate", secret_key="s"*48,
        seed_admin_email="test@example.com", seed_admin_password="test-admin-private"))
    sentinel = object()
    monkeypatch.setattr(cloud, "create_local_app", lambda: sentinel)
    assert cloud.create_cloud_app() is sentinel
