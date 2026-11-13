"""Validation over the curated 50-question dataset.

These assertions encode the presentation's proposed targets as *test
invariants* on the demo build. The measured values are recorded honestly in
docs/validation.md and reported by ``tests/run_validation.py``.
"""

import json
from pathlib import Path

import pytest

DATASET = json.loads(
    (Path(__file__).parent / "dataset" / "questions.json").read_text()
)["questions"]


def _ask(client, item):
    resp = client.post(
        "/chat", json={"question": item["question"], "context": item["context"]}
    )
    assert resp.status_code == 200
    return resp.json()


@pytest.mark.parametrize("item", DATASET, ids=[q["id"] for q in DATASET])
def test_dataset_answer_state(client, item):
    body = _ask(client, item)
    expected = item["expected_state"]
    if expected == "answered_or_escalated":
        assert body["state"] in {"answered", "escalated"}
    else:
        assert body["state"] == expected, (
            f"{item['id']}: expected {expected}, got {body['state']}"
        )


def test_zero_unsupported_guesses(client):
    unsupported = [q for q in DATASET if q["bucket"] == "unsupported"]
    guesses = [q["id"] for q in unsupported if _ask(client, q)["state"] == "answered"]
    assert guesses == [], f"unsupported questions were answered: {guesses}"


def test_citation_coverage_is_complete(client):
    answered = [q for q in DATASET if _ask(client, q)["state"] == "answered"]
    missing = [q["id"] for q in answered if not _ask(client, q)["citations"]]
    assert missing == [], f"answered without citation: {missing}"


def test_supported_answer_accuracy_meets_target(client):
    routine = [q for q in DATASET if q["bucket"] == "routine"]
    answered = [q for q in routine if _ask(client, q)["state"] == "answered"]
    accuracy = len(answered) / len(routine)
    assert accuracy >= 0.90, f"supported-answer accuracy {accuracy:.0%} below target"
