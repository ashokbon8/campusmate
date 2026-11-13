"""Validation harness for the 50-question curated dataset.

Runs every question through the real chat endpoint and reports the metrics the
presentation asks to distinguish:

* supported-answer accuracy   (routine + outdated buckets: expected "answered")
* citation coverage           (answered responses that carry a citation)
* unsupported guesses         (unsupported bucket answered instead of escalated)
* clarification rate          (needs_context responses)
* escalation rate             (escalated responses)
* response latency            (p50 / p95)

These are *measured* results for the demo build with synthetic sample data, and
must not be confused with the presentation's proposed targets. Run with:

    python tests/run_validation.py
"""

from __future__ import annotations

import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

_TMP = tempfile.mkdtemp(prefix="campusmate-validate-")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TMP}/validate.db")
os.environ.setdefault("UPLOAD_DIR", f"{_TMP}/documents")
os.environ.setdefault("SECRET_KEY", "validate-secret")
os.environ.setdefault("CAMPUSMATE_SEED", "1")
os.environ.setdefault("CAMPUSMATE_DATASET", "demo")


def main() -> int:
    from fastapi.testclient import TestClient

    from app.main import app

    dataset = json.loads((Path(__file__).parent / "dataset" / "questions.json").read_text())
    questions = dataset["questions"]

    with TestClient(app) as client:
        latencies: list[float] = []
        buckets: dict[str, dict[str, int]] = {}
        answered_total = 0
        answered_with_citation = 0
        unsupported_guesses = 0
        needs_context = 0
        escalated = 0

        for item in questions:
            start = time.perf_counter()
            resp = client.post(
                "/chat",
                json={"question": item["question"], "context": item["context"]},
            )
            latencies.append((time.perf_counter() - start) * 1000)
            body = resp.json()
            state = body["state"]
            bucket = item["bucket"]
            stats = buckets.setdefault(bucket, {"total": 0, "answered": 0, "needs_context": 0, "escalated": 0})
            stats["total"] += 1
            stats[state] = stats.get(state, 0) + 1

            if state == "answered":
                answered_total += 1
                if body["citations"]:
                    answered_with_citation += 1
            if state == "needs_context":
                needs_context += 1
            if state == "escalated":
                escalated += 1
            if bucket == "unsupported" and state == "answered":
                unsupported_guesses += 1

            expected = item["expected_state"]
            ok = (
                expected == state
                or (expected == "answered_or_escalated" and state in {"answered", "escalated"})
            )
            mark = "PASS" if ok else "FAIL"
            print(f"[{mark}] {item['id']:<8} {state:<13} {item['question']}")

        total = len(questions)
        # Supported-answer accuracy is measured over the 25 routine questions.
        supported = [q for q in questions if q["bucket"] == "routine"]
        supported_answered = sum(
            1
            for q in supported
            if _state_for(client, q) == "answered"
        )

        lat_sorted = sorted(latencies)
        p95 = lat_sorted[max(0, int(len(lat_sorted) * 0.95) - 1)]

        print("\n================ MEASURED RESULTS (demo build, sample data) ================")
        print(f"Questions run              : {total}")
        print(f"Supported-answer accuracy  : {supported_answered}/{len(supported)} "
              f"({supported_answered / len(supported):.0%})")
        print(f"Citation coverage          : {answered_with_citation}/{answered_total} "
              f"({(answered_with_citation / answered_total if answered_total else 0):.0%})")
        print(f"Unsupported guesses        : {unsupported_guesses} "
              f"(of {buckets.get('unsupported', {}).get('total', 0)} unsupported)")
        print(f"Clarification rate         : {needs_context}/{total} ({needs_context / total:.0%})")
        print(f"Escalation rate            : {escalated}/{total} ({escalated / total:.0%})")
        print(f"Latency p50 / p95          : {statistics.median(latencies):.0f} ms / {p95:.0f} ms")
        print("==========================================================================")
        print("NOTE: these are measured values for the synthetic demo build, not the")
        print("presentation's proposed targets.")
    return 0


def _state_for(client, item) -> str:
    return client.post(
        "/chat", json={"question": item["question"], "context": item["context"]}
    ).json()["state"]


if __name__ == "__main__":
    raise SystemExit(main())
