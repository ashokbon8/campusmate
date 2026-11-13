"""Document endpoints: public reads, source authorisation and draft protection."""


def test_list_documents_returns_published_notices(client):
    docs = client.get("/documents").json()
    assert docs
    assert all(d["status"] == "published" for d in docs)


def test_document_detail_includes_passages_and_source_status(client):
    doc_uid = client.get("/documents").json()[0]["doc_uid"]
    detail = client.get(f"/documents/{doc_uid}").json()
    assert detail["passages"], "extracted passages must be inspectable"
    assert detail["source_status"] in {"current", "replaced", "expired", "conflicting"}


def test_unknown_document_returns_404(client):
    assert client.get("/documents/does-not-exist").status_code == 404


def test_source_file_is_served_as_pdf(client):
    doc_uid = client.get("/documents").json()[0]["doc_uid"]
    resp = client.get(f"/documents/{doc_uid}/source")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"


def test_source_of_unknown_document_is_404(client):
    assert client.get("/documents/nope/source").status_code == 404


def test_source_is_regenerated_when_stored_file_is_gone(client):
    """Ephemeral hosts may lose the stored file; the source must still open."""
    import os

    doc_uid = client.get("/documents").json()[0]["doc_uid"]
    detail = client.get(f"/documents/{doc_uid}").json()

    # Simulate a serverless instance whose temp files were discarded.
    from app.database import SessionLocal
    from app.models import Document
    from sqlalchemy import select

    db = SessionLocal()
    try:
        document = db.scalar(select(Document).where(Document.doc_uid == doc_uid))
        stored_path = document.stored_path
        if stored_path and os.path.exists(stored_path):
            os.remove(stored_path)
    finally:
        db.close()

    resp = client.get(f"/documents/{doc_uid}/source")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"
    assert detail["passages"], "regeneration needs indexed passages"


def test_draft_documents_are_never_public(client, auth_headers):
    # Upload a draft (not published) and confirm it is hidden from students.
    files = {"file": ("draft.pdf", _minimal_pdf(), "application/pdf")}
    data = {"title": "Draft only notice", "category": "Fees", "doc_type": "pdf"}
    created = client.post("/admin/notices", data=data, files=files, headers=auth_headers)
    assert created.status_code == 201, created.text
    doc_uid = created.json()["doc_uid"]
    assert created.json()["status"] == "draft"

    public = client.get("/documents").json()
    assert all(d["doc_uid"] != doc_uid for d in public)
    assert client.get(f"/documents/{doc_uid}").status_code == 404
    assert client.get(f"/documents/{doc_uid}/source").status_code == 404


def _minimal_pdf() -> bytes:
    from app.services.pdf_writer import build_pdf

    return build_pdf(
        ["[SAMPLE] Draft notice", "Programme: BSc CS", "This is a draft body."]
    )
