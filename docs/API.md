# API Reference

Base URL in development: `http://localhost:8000`.
Through the frontend proxy: `/api`.

Interactive docs are served by FastAPI at `/docs` (Swagger) and `/redoc`.

Authentication uses a bearer JWT. Admin endpoints require the token; upload and
publish endpoints additionally require the `admin` or `publisher` role.

```
Authorization: Bearer <access_token>
```

---

## Meta

### `GET /health`
Liveness probe.

```json
{ "status": "ok", "environment": "development",
  "llm_provider": "stub", "embedding_provider": "hashing" }
```

### `GET /meta/categories`
Returns the five supported categories.

```json
{ "categories": ["Admissions", "Fees", "Examinations", "Timetables", "College activities"] }
```

---

## Student chat

### `POST /chat`
Answer a student question with citations, a clarification request, or an
escalation.

Request:

```json
{
  "question": "When is my exam?",
  "context": {
    "programme": "BSc CS",
    "semester": "1",
    "subject": "Mathematics",
    "academic_year": "2026-27",
    "history": []
  }
}
```

Response (`state = answered`):

```json
{
  "state": "answered",
  "answer": "The Mathematics examination will be held on 10 December 2026 at 10:00 AM in Room 204.",
  "clarification_question": null,
  "citations": [
    {
      "document_id": "examin-c4221958",
      "document_title": "Sample Mathematics examination notice (current)",
      "page": 1,
      "publication_date": "2026-11-03",
      "version": 2,
      "status": "published",
      "source_status": "current",
      "category": "Examinations",
      "excerpt": "The Mathematics examination will be held on 10 December 2026 ...",
      "open_url": "/api/documents/examin-c4221958/source"
    }
  ],
  "knowledge_version": "kv-0002",
  "category": "Examinations",
  "is_sample_data": true,
  "ticket_suggested": false
}
```

Response (`state = needs_context`):

```json
{
  "state": "needs_context",
  "answer": "I can help with that, but I need a little more information ...",
  "clarification_question": "Could you tell me your programme, your semester, and the subject? ...",
  "citations": [],
  "category": "Examinations",
  "ticket_suggested": false
}
```

Response (`state = escalated`):

```json
{
  "state": "escalated",
  "answer": "I could not find an approved notice that answers this ...",
  "citations": [],
  "category": null,
  "ticket_suggested": true
}
```

---

## Documents (public)

### `GET /documents?category=&status=`
List published notices. Optional filters: `category`, `status`.

### `GET /documents/{doc_uid}`
Document detail including extracted passages and `source_status`
(`current` | `replaced` | `expired` | `conflicting`). Drafts are not returned.

### `GET /documents/{doc_uid}/source`
Serve the source PDF. Draft documents are never served. Requires the document
to be published, replaced or retired.

---

## Admin — notices

All require `Authorization: Bearer`. Upload and publish require the
`admin`/`publisher` role.

### `GET /admin/notices`
List all notices (any status).

### `POST /admin/notices` — multipart/form-data
Upload a PDF or create an FAQ. Saved as `draft`.

| Field | Notes |
| --- | --- |
| `title` (required) | Document title |
| `category` (required) | One of the five categories |
| `doc_type` | `pdf` (default) or `faq` |
| `programme`, `academic_year`, `semester`, `subject` | Optional metadata filters |
| `publication_date`, `effective_date`, `expiry_date` | Optional dates |
| `source_page` | Optional page reference |
| `replaces_document_id` | Set to supersede an existing notice (increments version) |
| `body` | FAQ text (required when `doc_type=faq`) |
| `file` | PDF file (required when `doc_type=pdf`) |

### `GET /admin/notices/{doc_id}/extracted`
Review extracted passages and page references before publishing.

### `POST /admin/notices/{doc_id}/publish`
Publish an approved document version (re-indexes and activates the knowledge
version).

### `POST /admin/notices/{doc_id}/reindex`
Re-extract and re-index a document.

### `POST /admin/notices/{doc_id}/retire`
Retire an outdated notice.

### `GET /admin/notices/{doc_id}/versions`
Version history for a notice.

### `GET /admin/overview`
Dashboard metrics: total/published/replaced notices, pending/resolved tickets,
unanswered categories, active knowledge version. Returns `is_sample_data`.

---

## Helpdesk tickets

### `POST /tickets`
Create a ticket. Collects only the minimum information.

```json
{
  "student_name": "Sample Student",
  "contact": "student@example.com",
  "category": "Examinations",
  "programme": "BSc CS",
  "semester": "1",
  "subject": "Mathematics",
  "description": "My exam room is not listed.",
  "related_document_id": 12
}
```

Returns a ticket with a `reference` such as `CM-1A2B3C`.

### `GET /tickets/{reference}`
Student lookup by reference. Internal staff notes are filtered out.

### `GET /admin/tickets?status=&category=`
List tickets with optional filters (staff only).

### `GET /admin/tickets/{ticket_id}`
Ticket detail including messages (staff only).

### `POST /admin/tickets/{ticket_id}/messages`
Add a staff reply or internal note (`is_internal: true`) (staff only).

### `PATCH /admin/tickets/{ticket_id}`
Change status. Allowed: `open`, `pending`, `in_progress`, `resolved`, `closed`.

---

## Authentication

Two independent account types share the `/auth` prefix. Student routes are
public (self sign-up / sign-in); staff routes require a provisioned admin
account and never expose credentials through the API.

### `POST /auth/student/signup`
```json
{
  "full_name": "Asha Rao",
  "email": "asha@example.com",
  "password": "at-least-8-chars",
  "programme": "BSc CS",
  "semester": "1"
}
```
Creates a student account and returns
`{ "access_token": "...", "token_type": "bearer", "account": { ... } }`.
`409` if the email already exists; `422` if the password is shorter than 8
characters. The plain password is never returned — only a bcrypt hash is stored.

### `POST /auth/student/login`
```json
{ "email": "asha@example.com", "password": "at-least-8-chars" }
```
Returns the same token + account shape. `401` on bad credentials.

### `GET /auth/student/me`
Current authenticated student (`Authorization: Bearer <student token>`).

### `POST /auth/login`
Staff (admin) sign-in. Credentials are supplied through the deployment
environment (`SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`); none are published.
```json
{ "email": "<admin email>", "password": "<admin password>" }
```
Returns `{ "access_token": "...", "token_type": "bearer" }`.

### `POST /auth/token`
OAuth2 password-flow form login (same result as `/auth/login`; used by the
Swagger "Authorize" button).

### `GET /auth/me`
Current authenticated admin.

Student and admin tokens are not interchangeable: a student token is rejected by
admin routes (`/auth/me`, `/admin/*`) with `401`, and an admin token is rejected
by `/auth/student/me`.

---

## Error handling

Errors use standard FastAPI shape with meaningful HTTP status codes:
`400` bad request, `401` not authenticated, `403` insufficient role,
`404` not found, `413` file too large, `422` validation error.
