# Testing

Two layers: a pytest suite for the application, and a 50-question validation
harness that measures the chatbot against a curated dataset.

> **Important.** All numbers in this document describe the **synthetic demo
> build with offline stub models and sample data**. They are not real college
> performance, and they are separate from the presentation's *proposed targets*.

---

## Running

```bash
# from the repository root
python -m pytest                  # full suite
python tests/run_validation.py    # 50-question validation harness
```

The suite runs against a temporary SQLite database with deterministic stub
model adapters, so it needs no network and no API key.

---

## Test suite

| File | Focus |
| --- | --- |
| `test_health.py` | Health and category meta endpoints |
| `test_auth.py` | Login, token, role checks, protected routes |
| `test_chat.py` | Answer states: answered / needs_context / escalated, citations |
| `test_documents.py` | Upload, extraction, listing, source serving, draft protection |
| `test_publishing.py` | Publish, replace/version, retire, reindex, knowledge version |
| `test_tickets.py` | Ticket create, lookup, filtering, notes, status changes |
| `test_units.py` | Retrieval scoring, answer policy, sanitisation, evidence checks |
| `test_validation_dataset.py` | Runs the 50-question dataset and asserts policy guarantees |

Current result for this build: **132 tests passing**.

---

## Validation dataset

`tests/dataset/questions.json` holds 50 curated questions:

| Bucket | Count | Purpose |
| --- | --- | --- |
| Routine | 25 | Five from each of the five categories |
| Missing context | 10 | Should trigger a clarification question |
| Unsupported | 10 | Should escalate, never guess |
| Superseded / versioned | 5 | Should use the current notice, not the replaced one |

Each entry has a question, optional context, and an expected answer state.

---

## Measured results (demo build)

Produced by `python tests/run_validation.py` over the dataset above.

| Metric | Measured | Proposed target |
| --- | --- | --- |
| Supported-answer accuracy | 25 / 25 (100%) | 90%+ |
| Citation coverage | 26 / 26 (100%) | 100% |
| Unsupported guesses | 0 of 10 | 0 |
| Clarification rate | 10 / 50 (20%) | — |
| Escalation rate | 14 / 50 (28%) | — |
| Latency p50 / p95 | ~6 ms / ~9 ms (local) | ≤ 5 s |

Interpretation:

- **Supported-answer accuracy** — of the 25 routine questions, how many returned
  the expected supported answer.
- **Citation coverage** — every factual answer returned carried at least one
  citation.
- **Unsupported guesses** — answers produced for the 10 unsupported questions.
  Zero is the requirement; the harness asserts it.
- **Clarification / escalation rate** — the share of all 50 questions that
  triggered each path (these are behaviours, not pass/fail targets).
- **Latency** — measured locally with the deterministic stub model. A hosted
  model adds network time; re-run against the target deployment before quoting
  it.

---

## What is NOT claimed

- These are not results on real college documents or real student questions.
- Latency is local stub-model latency, not a hosted end-to-end measurement.
- No calibrated confidence score is exposed; the answer policy is
  evidence-based, not probabilistic.
- The system is not claimed to be hallucination-free or completely secure.

---

## Adding to the dataset

Add an object to `questions[]` in `tests/dataset/questions.json`:

```json
{
  "id": "R-EXM-6",
  "bucket": "routine",
  "category": "Examinations",
  "question": "When is the Physics exam?",
  "context": { "programme": "BSc CS", "semester": "1", "subject": "Physics" },
  "expected_state": "answered"
}
```

`expected_state` is one of `answered`, `needs_context`, `escalated`, or
`answered_or_escalated` (for cases that may legitimately go either way).
