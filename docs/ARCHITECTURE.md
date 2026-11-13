# Architecture

CampusMate is a retrieval-augmented helpdesk. A student question is matched
against approved college notices; the answer is drafted only from the retrieved
evidence and is returned with a citation, a clarifying question, or an
escalation to a helpdesk ticket.

## Components

```
┌──────────────────────────────┐        ┌────────────────────────────────────┐
│  Frontend (React + Vite)     │  HTTP  │  Backend (FastAPI)                 │
│                              │ /api/* │                                    │
│  Home intro / Auth / Chat    │ ─────▶ │  routers/                          │
│  Noticeboard / Tickets       │        │    chat · documents · tickets · auth│
│  Admin workspace             │ ◀───── │  services/                         │
│                              │  JSON  │    retrieval · answer_policy        │
└──────────────────────────────┘        │    chat · publishing · documents    │
                                        │    llm · embeddings · seed          │
                                        └───────────────┬────────────────────┘
                                                        │ SQLAlchemy
                                        ┌───────────────▼────────────────────┐
                                        │  PostgreSQL + pgvector              │
                                        │  (SQLite + JSON vectors for demo)   │
                                        │                                    │
                                        │  admins · students · knowledge_     │
                                        │  versions · documents · passages    │
                                        │  tickets · ticket_messages          │
                                        │  chat_logs                          │
                                        └────────────────────────────────────┘
```

## Backend layers

| Layer | Files | Responsibility |
| --- | --- | --- |
| Routers | `app/routers/*` | HTTP endpoints, validation, auth dependencies |
| Services | `app/services/*` | Business logic: retrieval, answer policy, publishing, chat orchestration |
| Models | `app/models.py` | SQLAlchemy tables and the portable embedding column |
| Schemas | `app/schemas.py` | Pydantic request/response contracts |
| Security | `app/security.py` | Password hashing, JWT, role checks |
| Config | `app/config.py` | Environment-driven settings |

## Retrieval-augmented generation flow

**Indexing an approved notice**

1. Administrator uploads a PDF or FAQ and enters metadata.
2. `documents.py` extracts readable text and page numbers (pypdf for PDFs).
3. Injection-style text is neutralised (`sanitize_passage`).
4. Metadata is attached (programme, year, semester, subject, dates, version).
5. Passages are embedded (`embeddings.py`) and stored in `passages`.
6. Publishing activates a new `KnowledgeVersion` and re-indexes.

**Answering a student question** (`services/chat.py`)

1. Receive the question and any supplied context.
2. Identify the category (`answer_policy.py`).
3. Check for missing required context (programme / semester / subject).
   If missing → `needs_context` with a clarification question.
4. Retrieve current, applicable passages — hybrid keyword + vector search with
   metadata filters and expiry filtering (`retrieval.py`).
5. Require a minimum evidence score and coverage before answering.
6. Draft an answer strictly from the retrieved evidence (`llm.py`).
7. Validate the draft against the evidence; if it cannot be supported → escalate.
8. Return `answered` with citations, or `escalated` with a ticket suggestion.

## Answer states

| State | Meaning | UI behaviour |
| --- | --- | --- |
| `answered` | Supported answer with citation(s) | Show answer + source card |
| `needs_context` | Required detail missing | Ask a clarification question |
| `escalated` | No approved answer, or conflicting | Explain the limit, offer a ticket |

## Document version workflow

Replacing a notice never removes the working information before the replacement
is ready:

1. Upload the new notice (saved as `draft`).
2. Validate metadata and extracted text.
3. Create the new knowledge version.
4. Re-index the document.
5. Confirm the new index is ready.
6. Switch the active knowledge version.
7. Retire the previous notice (`status = replaced`).
8. Old-version answers are no longer retrieved (cache/answer invalidation by
   knowledge-version scoping).

## Model adapters

`llm.py` and `embeddings.py` define provider interfaces with two
implementations each:

- `stub` / `hashing` — deterministic, offline, no API key. Used for the demo and
  for tests, so the app never depends on a paid service to run.
- `openai` — hosted models via a configurable base URL.

Switching provider is a configuration change only. API keys are read from
environment variables server-side and are never sent to the frontend.

## Security controls

- Two account types: public **student** sign-up/sign-in and provisioned staff
  (**admin**) accounts. Passwords are bcrypt-hashed; only hashes are stored.
- The chatbot, noticeboard and helpdesk tickets require a signed-in student; the
  public home intro is the only unauthenticated page with content.
- Admin credentials are supplied through the deployment environment, never
  committed to the repository and never shown or pre-filled in the UI.
- Student and admin JWTs are scoped by role: a student token cannot reach
  `/admin/*` or `/auth/me`, and an admin token cannot reach `/auth/student/me`.
- Staff authentication (JWT) with role checks; upload/publish require the
  `admin` or `publisher` role.
- Document-level authorisation before retrieval and before serving source files.
- Public notices are separated from private student records; no personal
  records are placed in the public retrieval index.
- AI credentials stored server-side only.
- Minimal ticket data collection and a defined retention approach (below).
- Prompt-injection content inside uploaded documents is neutralised before
  indexing.
- Evidence checking for dates, fees and examination details before an answer is
  returned.

## Data retention (proposed)

Tickets hold only the minimum contact detail needed to respond. The proposed
policy is to retain resolved tickets for one academic year and then archive or
delete them; unresolved tickets are retained until closed. This is a documented
policy, not an automated job in this MVP.

## Limitations

- Not claimed to be hallucination-free or completely secure.
- English text only.
- The demo runs with synthetic sample data and offline stub models.
