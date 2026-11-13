# Requirements traceability

Maps the MASTER PROMPT requirements to where they are implemented, and states
honestly what is delivered, what is synthetic demo data, what is a proposed
target, and what is future roadmap.

> The referenced PPTX was **not available** in the build environment. The
> project identity, the five categories, the example conversation, the
> architecture and the demo sequence were taken from the prompt specification,
> which reproduces the presentation's content. Where the presentation would have
> supplied a visual asset (e.g. the 3D assistant), a clearly-identified
> placeholder is used and can be replaced.

Legend: **✅ delivered** · **🧪 synthetic demo data** · **🎯 proposed target** ·
**🧭 future roadmap**

## 1. Project overview and identity

| Requirement | Status | Where |
| --- | --- | --- |
| CampusMate — Smart Student Helpdesk Chatbot | ✅ | `README.md`, `frontend/src/components/Header.jsx` |
| Primary message "A helpdesk students can verify." | ✅ | `frontend/src/pages/Landing.jsx` |
| Supporting message "Official information with a source and a clear next step." | ✅ | `frontend/src/components/Footer.jsx`, Landing |
| Not IoT/robotics; a software web application | ✅ | whole repo |

## 2. Critical requirements

| Requirement | Status | Where |
| --- | --- | --- |
| Preserve project identity and core concept | ✅ | README, Landing, Header |
| Five student-information categories | ✅ | `answer_policy.py`, `sampleData.js`, Landing |
| Student chatbot + authenticated admin workspace | ✅ | `frontend/src/pages/ChatPage.jsx`, `AdminWorkspace.jsx` |
| Answers based on college-approved information | ✅ | `services/chat.py`, `services/retrieval.py` |
| Display source notice, page, publication date, version | ✅ | `schemas.py` `Citation`, `SourceCard.jsx` |
| Ask clarification when context is missing | ✅ | `services/answer_policy.py`, `chat.py` |
| Never invent dates/fees/timetables | ✅ | evidence checks in `chat.py`; `test_chat.py` |
| Helpdesk ticket option when missing/conflicting/unsupported | ✅ | `routers/tickets.py`, `ChatPanel.jsx` |
| Document publishing, version management, outdated handling | ✅ | `services/publishing.py`, `routers/documents.py` |
| Responsive desktop/tablet/mobile | ✅ | `frontend/src/styles.css`, `components.css` |
| Modular, GitHub-ready code | ✅ | repo structure, `docs/` |
| Do not present synthetic data as real | 🧪 | sample tags throughout, `docs/DEMO_DATA.md` |

## 3. Design and visual direction

| Requirement | Status | Where |
| --- | --- | --- |
| Modern academic tech look, strong hierarchy | ✅ | `styles.css`, `components.css` |
| Cards, smooth transitions, restrained gradients | ✅ | Landing, Chat, Admin |
| 3D assistant asset, or clearly-identified placeholder | ✅ | `components/Mascot.jsx` (replaceable placeholder) |
| Accessible contrast, readable text | ✅ | theme tokens; contrast/large-text options |

## 4. Website structure

| Section | Status | Where |
| --- | --- | --- |
| Landing: branding, heading, problem, CTAs, preview, categories, verification, contact, footer | ✅ | `pages/Landing.jsx`, `Footer.jsx` |
| "Ask CampusMate" and "How it works" buttons | ✅ | `Landing.jsx` |
| Chatbot preview | ✅ | `Landing.jsx` |
| Source-verification section | ✅ | `Landing.jsx` |
| Contact-the-office section | ✅ | `Landing.jsx` |
| Student information problem (3 items) | ✅ | `sampleData.js` `PROBLEMS` |
| How CampusMate works (3-step workflow) | ✅ | `sampleData.js` `WORKFLOW`, `pages/HowItWorks.jsx` |
| No invented survey statistics | ✅ | wording avoids unverified figures |

## 5. Five categories

| Category | Example question | Status | Where |
| --- | --- | --- | --- |
| Admissions | "Which documents do I need?" | ✅ | `answer_policy.py`, seed |
| Fees | "When is the next fee deadline?" | ✅ | seed; no private balances (enforced wording) |
| Examinations | "When is my Mathematics exam?" | ✅ | seed v1→v2 |
| Timetables | "Where is my next class?" | ✅ | seed |
| College activities | "How do I register for an event?" | ✅ | seed |
| Each with card, icon, description, example questions | ✅ | `Landing.jsx` |

## 6. Chatbot interface and behaviour

| Requirement | Status | Where |
| --- | --- | --- |
| Avatar, conversation area, bubbles, input, send | ✅ | `components/ChatPanel.jsx` |
| Loading indicator, clear chat, example buttons | ✅ | `ChatPanel.jsx` |
| Source citation panel, ticket action, clarification flow | ✅ | `ChatPanel.jsx`, `SourceCard.jsx` |
| Follow retrieval → clarify → retrieve → validate → cite → escalate sequence | ✅ | `services/chat.py` |
| Answer states answered / needs_context / escalated | ✅ | `schemas.py` `AnswerState`, `AnswerStateBadge.jsx` |
| No unsupported answers, no fabricated citations | ✅ | `answer_policy.py`, `chat.py`, `test_chat.py` |

## 7. Source citation and document viewer

| Requirement | Status | Where |
| --- | --- | --- |
| Source card: name, page, date, version, status, open button | ✅ | `SourceCard.jsx` |
| Open document at page (PDF viewer) | ✅ | `SourceViewer.jsx`, `/documents/{uid}/source` |
| Distinguish current / replaced / expired / conflicting | ✅ | `source_status`, `SourceViewer.jsx` |
| Do not fabricate document names/dates/pages | ✅ | citations come from stored metadata |

## 8. Example conversation

| Requirement | Status | Where |
| --- | --- | --- |
| Reproduce the PPTX example conversation | 🧪 | `sampleData.js` `SAMPLE_CONVERSATION`, seed, `docs/DEMO_DATA.md` |
| Clearly labelled as sample | 🧪 | sample tags, docs |

## 9. Retrieval-augmented generation

| Requirement | Status | Where |
| --- | --- | --- |
| Admin approves → extract text/pages → metadata → index | ✅ | `services/documents.py`, `publishing.py` |
| Metadata fields (id, title, programme, year, semester, subject, dates, version, status, page) | ✅ | `models.py` `Document`, `Passage` |
| Student flow: receive → missing context → clarify → retrieve → draft → validate → cite → escalate | ✅ | `services/chat.py` |
| Keyword + vector hybrid retrieval | ✅ | `services/retrieval.py`, `embeddings.py` |
| Metadata filters for programme/semester/validity | ✅ | `retrieval.py` |
| Treat document content as untrusted | ✅ | `documents.py` `sanitize_passage` |
| No uncalibrated confidence scores exposed | ✅ | no confidence field in `Citation`/`ChatResponse` |

## 10. Administrator dashboard

| Requirement | Status | Where |
| --- | --- | --- |
| Overview: uploaded, published, replaced, pending/resolved tickets, unanswered categories | ✅ | `/admin/overview`, `AdminWorkspace.jsx` |
| Upload PDFs and FAQs, metadata, review text/pages | ✅ | `UploadForm`, `/admin/notices/{id}/extracted` |
| Approve, publish, replace, versions, retire, re-index | ✅ | `routers/documents.py`, `AdminWorkspace.jsx` |
| Version workflow (never remove working info before replacement ready) | ✅ | `services/publishing.py` |
| Auth + role-based permissions; admin separate from public | ✅ | `security.py`, `require_publisher` |
| Demo metrics clearly labelled sample | 🧪 | `is_sample_data` flag |

## 11. Helpdesk tickets

| Requirement | Status | Where |
| --- | --- | --- |
| Create ticket when missing/unclear/conflicting/assistance needed | ✅ | `routers/tickets.py`, `Tickets.jsx` |
| Ticket form fields (name, contact, category, programme, semester, subject, description, related doc) | ✅ | `schemas.py` `TicketCreate` |
| Statuses open/pending/in_progress/resolved/closed | ✅ | `models.py` `Ticket`, `TicketStatusUpdate` |
| Admin: view, filter, detail, internal note, respond, change status, resolve | ✅ | `routers/tickets.py`, `AdminWorkspace.jsx` |
| Do not expose private ticket info publicly | ✅ | internal notes filtered in student lookup |

## 12. Full-stack architecture

| Requirement | Status | Where |
| --- | --- | --- |
| React frontend | ✅ | `frontend/` |
| FastAPI backend | ✅ | `backend/` |
| PostgreSQL + pgvector | ✅ | `database/schema.sql`, `models.py` |
| Embedding model + LLM with adapter | ✅ | `services/embeddings.py`, `services/llm.py` |
| No API secrets in frontend | ✅ | env-driven; server-side keys |
| Docker + documented deployment | ✅ | `docker-compose.yml`, `Dockerfile.*`, `docs/SETUP.md` |

## 13. API endpoints

| Endpoint | Status |
| --- | --- |
| `POST /chat` | ✅ |
| `POST /admin/notices` | ✅ |
| `POST /admin/notices/{id}/publish` | ✅ |
| `POST /tickets` | ✅ |
| Ticket listing / updates | ✅ |
| Document retrieval / version history | ✅ |
| Admin authentication (`/auth/login`, `/auth/token`, `/auth/me`) | ✅ |
| Validation and error handling | ✅ |

## 14. Security and trust

| Requirement | Status | Where |
| --- | --- | --- |
| Staff authentication, role checks | ✅ | `security.py` |
| Document-level authorisation before retrieval / serving | ✅ | `routers/documents.py` |
| Public notices separated from private records | ✅ | models + access checks |
| Secure server-side AI credentials | ✅ | config/env |
| Minimal ticket info; retention policy | ✅ | `TicketCreate`, `docs/ARCHITECTURE.md` |
| Cache/answer invalidation on version change | ✅ | knowledge-version scoping |
| Prompt-injection protection in uploads | ✅ | `sanitize_passage` |
| Evidence checking for dates/fees/exams | ✅ | `services/chat.py` |
| Not claimed zero-hallucination / fully secure | ✅ | README, docs |

## 15. 90-second demo

| Requirement | Status | Where |
| --- | --- | --- |
| Demo sequence built and runnable | ✅ | `docs/DEMO_SCRIPT.md` (verified end-to-end) |

## 16. MVP and roadmap

| Requirement | Status |
| --- | --- |
| English chat, PDFs+FAQs, source pages, version checks, admin publishing, tickets, clarification, safe fallback | ✅ |
| Hindi/Marathi support | 🧭 future |
| Opt-in deadline reminders | 🧭 future |
| Student portal integration | 🧭 future |
| Staff review of unanswered topics | 🧭 future |

## 17. Validation and testing

| Requirement | Status | Where |
| --- | --- | --- |
| Proposed targets (90%+, 100% citation, 0 guesses, p95 ≤ 5s) | 🎯 | `docs/TESTING.md`, `pages/TestingPlan.jsx` |
| 50-question dataset (25 routine / 10 missing context / 5 outdated / 10 unsupported) | ✅ | `tests/dataset/questions.json` |
| Measure supported accuracy, citation coverage, clarification, escalation, latency | ✅ | `tests/run_validation.py` |
| Record results honestly; keep separate from targets | ✅ | `docs/TESTING.md`, TestingPlan page |
| Not display targets as achieved results | ✅ | UI + docs wording |

Measured on this demo build: supported-answer accuracy 25/25 (100%), citation
coverage 26/26 (100%), unsupported guesses 0/10, latency p95 ~7 ms (local stub).

## 18. Anonymous presentation mode

| Requirement | Status |
| --- | --- |
| No college-identifying branding | ✅ |
| No personal names/IDs | ✅ (sample data uses generic labels) |
| No invented GitHub URL or live deployment URL | ✅ (placeholders only) |
| Remains a software web application | ✅ |

## 19. Code quality and GitHub readiness

| Requirement | Status | Where |
| --- | --- | --- |
| Repository structure as specified | ✅ | see README layout |
| Modular React components, reusable UI | ✅ | `frontend/src/components` |
| Frontend/backend separation | ✅ | `frontend/`, `backend/` |
| Environment variables for secrets | ✅ | `.env.example`, `.gitignore` |
| DB schema and migrations | ✅ | `database/schema.sql`, `backend/alembic/` |
| API documentation | ✅ | `docs/API.md`, FastAPI `/docs` |
| Setup / local dev / Docker / test instructions | ✅ | `docs/SETUP.md`, `docs/TESTING.md` |
| README | ✅ | `README.md` |
| No real secrets committed | ✅ | `.gitignore`, env-driven config |

## 20–21. Implementation process and final result

Delivered as specified: frontend, FastAPI backend, PostgreSQL schema, document
processing, retrieval and citations, clarification, publishing and version
management, ticket management, auth, connected frontend/backend, synthetic demo
data, tests, and documentation.

## Requirements not fully met / notes

- **PPTX asset**: the presentation file was not present, so the 3D assistant is
  a labelled placeholder (`components/Mascot.jsx`) intended to be swapped for
  the real asset.
- **Visual identity**: reproduced from the specification and the existing
  CampusMate stylesheet (dark, gradient-accent academic-tech look) rather than
  the unavailable slide deck.
- **PostgreSQL path**: schema and migrations are provided; the pgvector path is
  wired and was exercised end-to-end against a real `pgvector/pgvector:pg16`
  container via docker-compose (health, seed, and chat with citation all
  confirmed). A pgvector embedding is a numpy array, so `cosine()` normalises
  both lists and arrays — never call `bool()` on an embedding.
- **Hosted models**: adapters exist; the demo runs with offline stub models, so
  latency figures are local, not hosted.
