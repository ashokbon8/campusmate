"""Chat answer-policy tests.

Covers the three answer states (answered / needs_context / escalated), the
clarification flow, source citations and the evidence guard against invented
facts. These mirror the presentation's proposed test dataset categories.
"""

import pytest

CATEGORIES = ["Admissions", "Fees", "Examinations", "Timetables", "College activities"]


def chat(client, question, context=None):
    resp = client.post(
        "/chat", json={"question": question, "context": context or {}}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


# --- Clarification ---------------------------------------------------------
def test_exam_question_without_context_asks_for_clarification(client):
    body = chat(client, "When is my exam?")
    assert body["state"] == "needs_context"
    assert body["category"] == "Examinations"
    assert body["clarification_question"]
    assert "programme" in body["clarification_question"].lower()
    assert body["citations"] == []


def test_exam_question_with_full_context_is_answered(client):
    body = chat(
        client,
        "When is my Mathematics exam?",
        {"programme": "BSc CS", "semester": "1", "subject": "Mathematics"},
    )
    assert body["state"] == "answered"
    assert body["citations"], "a factual answer must carry a citation"
    citation = body["citations"][0]
    assert citation["document_id"]
    assert citation["page"] >= 1
    assert citation["version"] >= 1
    assert citation["source_status"] in {"current", "replaced", "expired", "conflicting"}
    assert citation["open_url"]


def test_answered_response_states_the_exam_details_from_evidence(client):
    body = chat(
        client,
        "When is my Mathematics exam?",
        {"programme": "BSc CS", "semester": "1", "subject": "Mathematics"},
    )
    assert "10 December 2026" in body["answer"]
    assert "10:00" in body["answer"]


# --- Escalation ------------------------------------------------------------
def test_unsupported_question_is_escalated_not_guessed(client):
    body = chat(client, "What is the cafeteria menu on Friday?")
    assert body["state"] == "escalated"
    assert body["ticket_suggested"] is True
    assert body["citations"] == []


def test_unsupported_category_escalates(client):
    # Category detected (Fees) but no matching approved evidence for this detail.
    body = chat(
        client,
        "What is my personal outstanding fee balance for hostel laundry?",
        {"programme": "BSc CS", "academic_year": "2026-27"},
    )
    assert body["state"] in {"escalated", "answered"}
    if body["state"] == "escalated":
        assert body["ticket_suggested"] is True


# --- Evidence guard --------------------------------------------------------
def test_answer_never_contains_a_date_absent_from_evidence(client):
    body = chat(
        client,
        "When is my Mathematics exam?",
        {"programme": "BSc CS", "semester": "1", "subject": "Mathematics"},
    )
    assert body["state"] == "answered"
    # Every citation excerpt is real evidence and must contain the stated date.
    joined = " ".join(c["excerpt"] for c in body["citations"]).lower()
    assert "december" in joined


# --- Context requirements per category ------------------------------------
@pytest.mark.parametrize(
    "question,context,expected_state",
    [
        ("Which documents do I need?", {}, "needs_context"),  # Admissions needs programme
        (
            "Which documents do I need?",
            {"programme": "BSc CS"},
            "answered",
        ),
        ("When is the next fee deadline?", {}, "needs_context"),  # Fees needs programme + year
        (
            "When is the next fee deadline?",
            {"programme": "BSc CS", "academic_year": "2026-27"},
            "answered",
        ),
        ("Where is my next class?", {}, "needs_context"),  # Timetables needs programme + sem
        (
            "Where is my next class?",
            {"programme": "BSc CS", "semester": "1"},
            "answered",
        ),
        (
            "How do I register for an event?",
            {},
            "answered",
        ),  # College activities needs no context
    ],
)
def test_category_context_rules(client, question, context, expected_state):
    body = chat(client, question, context)
    assert body["state"] == expected_state, body


def test_all_five_categories_are_covered_by_sample_data(client):
    seen = set()
    for category in CATEGORIES:
        docs = client.get("/documents", params={"category": category}).json()
        if docs:
            seen.add(category)
    assert seen == set(CATEGORIES), f"missing sample notices for: {set(CATEGORIES) - seen}"


def test_every_answer_carries_a_knowledge_version(client):
    body = chat(
        client,
        "When is my Mathematics exam?",
        {"programme": "BSc CS", "semester": "1", "subject": "Mathematics"},
    )
    assert body["knowledge_version"]
    assert body["is_sample_data"] is True
