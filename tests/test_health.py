"""Health and metadata endpoints."""


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["llm_provider"] == "stub"
    assert body["embedding_provider"] == "hashing"


def test_categories_match_the_five_presentation_categories(client):
    resp = client.get("/meta/categories")
    assert resp.status_code == 200
    assert resp.json()["categories"] == [
        "Admissions",
        "Fees",
        "Examinations",
        "Timetables",
        "College activities",
    ]
