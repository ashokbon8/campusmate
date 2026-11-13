"""Document publishing, replacement and knowledge-version workflow.

These tests mirror the presentation's version workflow: upload a replacement,
confirm the new index is ready, publish (which activates a new knowledge
version and retires the previous notice), and confirm the chatbot now uses the
updated notice.
"""


def _find_exam(client, auth_headers):
    notices = client.get("/admin/notices", headers=auth_headers).json()
    published = [
        n
        for n in notices
        if n["category"] == "Examinations" and n["status"] == "published"
    ]
    assert published, "expected a published examination notice"
    return published[0]


def test_upload_indexes_passages_and_stays_draft(client, auth_headers):
    from app.services.pdf_writer import build_pdf

    pdf = build_pdf(
        [
            "[SAMPLE] Library timing notice",
            "Programme: BSc CS",
            "The library is open from 08:00 to 20:00 on weekdays.",
        ]
    )
    resp = client.post(
        "/admin/notices",
        data={
            "title": "Library timing (sample)",
            "category": "College activities",
            "doc_type": "pdf",
        },
        files={"file": ("library.pdf", pdf, "application/pdf")},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    doc = resp.json()
    assert doc["status"] == "draft"

    extracted = client.get(
        f"/admin/notices/{doc['id']}/extracted", headers=auth_headers
    ).json()
    assert extracted, "extracted text must be reviewable before publishing"


def test_reindex_reports_ready(client, auth_headers):
    doc = _find_exam(client, auth_headers)
    resp = client.post(
        f"/admin/notices/{doc['id']}/reindex", headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["passages_indexed"] >= 1
    assert "ready" in body["message"].lower()


def test_publishing_a_replacement_updates_the_chatbot_answer(client, auth_headers):
    from app.services.pdf_writer import build_pdf

    before = client.post(
        "/chat",
        json={
            "question": "When is my Mathematics exam?",
            "context": {"programme": "BSc CS", "semester": "1", "subject": "Mathematics"},
        },
    ).json()
    assert before["state"] == "answered"
    old_version = before["citations"][0]["version"]

    target = _find_exam(client, auth_headers)

    pdf = build_pdf(
        [
            "[SAMPLE] Mathematics examination notice (revised)",
            "Programme: BSc CS | Semester: 1 | Subject: Mathematics",
            "The Mathematics examination will now be held on 15 December 2026 at "
            "02:00 PM in Room 305.",
        ]
    )
    uploaded = client.post(
        "/admin/notices",
        data={
            "title": "Mathematics exam notice (revised sample)",
            "category": "Examinations",
            "programme": "BSc CS",
            "semester": "1",
            "subject": "Mathematics",
            "publication_date": "2026-11-08",
            "replaces_document_id": str(target["id"]),
        },
        files={"file": ("revised.pdf", pdf, "application/pdf")},
        headers=auth_headers,
    )
    assert uploaded.status_code == 201, uploaded.text
    new_doc = uploaded.json()
    assert new_doc["version"] == old_version + 1

    published = client.post(
        f"/admin/notices/{new_doc['id']}/publish", headers=auth_headers
    )
    assert published.status_code == 200, published.text

    # The previous notice is now marked replaced.
    after_target = client.get("/documents").json()
    replaced_ids = {
        d["doc_uid"] for d in after_target if d["status"] == "published"
    }
    assert new_doc["doc_uid"] in replaced_ids

    after = client.post(
        "/chat",
        json={
            "question": "When is my Mathematics exam?",
            "context": {"programme": "BSc CS", "semester": "1", "subject": "Mathematics"},
        },
    ).json()
    assert after["state"] == "answered"
    assert "15 December 2026" in after["answer"]
    assert after["citations"][0]["version"] == old_version + 1


def test_version_history_links_the_replace_chain(client, auth_headers):
    target = _find_exam(client, auth_headers)
    versions = client.get(
        f"/admin/notices/{target['id']}/versions", headers=auth_headers
    ).json()
    assert len(versions) >= 2, "expected at least a superseded and a current version"
    numbers = [v["version"] for v in versions]
    assert numbers == sorted(numbers)


def test_overview_reports_knowledge_version_and_counts(client, auth_headers):
    stats = client.get("/admin/overview", headers=auth_headers).json()
    assert stats["total_notices"] >= 1
    assert stats["published_notices"] >= 1
    assert stats["replaced_notices"] >= 1
    assert stats["active_knowledge_version"]
    assert stats["is_sample_data"] is True


def test_retiring_a_notice_marks_it_expired(client, auth_headers):
    from app.services.pdf_writer import build_pdf

    pdf = build_pdf(["[SAMPLE] Temporary notice", "This notice will be retired."])
    created = client.post(
        "/admin/notices",
        data={"title": "Temporary (sample)", "category": "Fees", "doc_type": "pdf"},
        files={"file": ("temp.pdf", pdf, "application/pdf")},
        headers=auth_headers,
    ).json()
    client.post(f"/admin/notices/{created['id']}/publish", headers=auth_headers)
    retired = client.post(
        f"/admin/notices/{created['id']}/retire", headers=auth_headers
    )
    assert retired.status_code == 200
    assert retired.json()["status"] == "retired"
