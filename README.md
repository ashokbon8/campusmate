# CampusMate — Smart Student Helpdesk Chatbot

**A helpdesk students can verify.**

**Source code:** https://github.com/ashokbon8/campusmate

## Hackathon submission and live website

To upload this full release to your repository from VS Code, run
`.\UPLOAD_TO_GITHUB.cmd` and finish Git's browser sign-in if prompted. The helper
uploads only release files and excludes your private local data.

Submit the GitHub repository containing this final source. The online deployment
configuration is included: `render.yaml` creates one full-stack web service and
a PostgreSQL database. Read [PUBLISH_ONLINE.md](PUBLISH_ONLINE.md) for GitHub and
publishing steps. Add the confirmed live URL here and in the repository's About
section after deployment. No live deployment is claimed by this source archive.

The supplied hosting configuration uses free instances. Free Render PostgreSQL
expires after 30 days; free web services sleep when idle. Choose hosting that
lasts through your judging date. New PDF uploads are retained in the database
so they survive a web-service restart.

## Final ZIP: one-command local startup

Open the extracted final ZIP folder in VS Code, then run
`.\RUN_CAMPUSMATE.cmd`. It installs Python requirements, asks for your admin
login on the first launch and opens http://localhost:5173. The final ZIP bundles
the built React website, which is also included in this GitHub repository, so
normal local use needs Python 3.12/3.11 and does not need Node.js. The sections
below also document the source development and
deployment options. See [START_HERE.md](START_HERE.md) for the complete guide.

Midnight black, pure white and lime green throughout. **Admin Login** is visible
in the header and footer. On Windows, run `RUN_CAMPUSMATE.cmd`; administrator
setup is included on the first launch.
See [START_HERE.md](START_HERE.md) for installation and update steps.

CampusMate answers student questions about college notices and always shows the
official source it used: document name, page, publication date, version and
status. When the approved information cannot answer a question, CampusMate asks
for the missing details or offers a helpdesk ticket. It does not invent
examination dates, fee deadlines or timetables.

> **JSCOE college data is included.** The default startup imports 29 sourced FAQs
> from the college website, checked on 13 November 2026. Admission information,
> posted 2026–27 programme/category fees and the complete first-year odd-semester
> calendar are ready to query. Examination-page listings from 2024/2025 are
> labelled historical. [Start here](START_HERE.md) or read [the data guide](docs/JSCOE_DATA.md).
> Synthetic fixtures remain available only with `CAMPUSMATE_DATASET=demo` for the
> original presentation and regression suite.

---

## What is in this repository

| Area | Technology | Location |
| --- | --- | --- |
| Student chatbot, landing page, source viewer, admin workspace | React + Vite | `frontend/` |
| Chat, retrieval, publishing, tickets, auth | FastAPI | `backend/` |
| Approved notices, versions, passages, tickets | PostgreSQL + pgvector (SQLite for zero-setup demo) | `database/` |
| Test suite + 50-question validation harness | pytest | `tests/` |
| Documentation | Markdown | `docs/` |

Full architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
API reference: [docs/API.md](docs/API.md).

---

## Features

**Student side**

- Public home intro page before sign-in, with sign-up / sign-in entry points.
- Self-service student accounts (sign-up and sign-in); the chatbot, noticeboard
  and helpdesk tickets are available once signed in.
- Natural-language chat across five official categories: **Admissions, Fees,
  Examinations, Timetables, College activities**.
- Three explicit answer states: `answered`, `needs_context`, `escalated`.
- Clarification flow — CampusMate asks for programme / semester / subject
  before giving a specific answer.
- Every factual answer carries a source card (document, page, date, version,
  status) and an openable source document.
- Helpdesk ticket creation when information is missing, conflicting or unclear.
- Noticeboard, "How it works" explainer and a validation/testing page.
- Responsive layout, dark/light theme, larger-text, high-contrast and
  reduce-motion accessibility options.

**Administrator side**

- Token-based login with role checks (`admin` / `publisher` may publish;
  `viewer` may only read).
- Overview metrics (uploaded, published, replaced, pending/resolved tickets).
- Upload PDFs and FAQs with metadata, review extracted text and page references.
- Approve, publish, replace, retire documents; inspect version history;
  trigger re-indexing.
- Ticket queue with filtering, internal notes, replies and status changes.

**Trust and safety**

- Answers are built only from retrieved, approved evidence and validated
  against it before being returned.
- Unsupported questions are escalated, never guessed.
- Prompt-injection text inside uploaded documents is neutralised.
- Model adapters keep AI credentials server-side; secrets come from env vars.

---

## Quick start (local, zero external services)

Runs with SQLite and offline stub model adapters — no API key or database
server needed. Requires **Python 3.11+** and **Node.js 18+**.

```bash
# 1. Backend
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
#    -> http://localhost:8000/docs   (interactive API docs)

# 2. Frontend (in a second terminal)
cd frontend
npm install
npm run dev
#    -> http://localhost:5173
```

The first backend start imports the JSCOE data pack automatically. Students
create their own account from the **Create account** page; staff sign in to the
admin workspace with credentials supplied through the environment.

> **Admin credentials are private.** No admin email or password is shown in the
> UI or committed to the repository. Set `SEED_ADMIN_EMAIL` /
> `SEED_ADMIN_PASSWORD` (and `SECRET_KEY`) in your environment before deploying,
> and keep them out of source control.

---

## Docker (PostgreSQL + pgvector)

```bash
cp .env.example .env          # review values; never commit .env
docker compose up --build
#    -> frontend  http://localhost:8080
#    -> backend   http://localhost:8000/docs
```

`docker-compose.yml` runs three services: `db` (pgvector image), `backend`
(FastAPI) and `frontend` (static build served by nginx, which proxies `/api` to
the backend). See [docs/SETUP.md](docs/SETUP.md) for details.

---

## Deploy on Vercel (services)

The root `vercel.json` deploys both the FastAPI backend and the Vite frontend as
services in one Vercel project. `/api/*` routes to the backend and every other
path to the frontend, on the same domain:

```bash
vercel dev      # run both services locally
vercel --prod   # deploy
```

The app detects Vercel automatically and uses `/api` as its route prefix plus
`/tmp` for its writable files, so the demo works after deployment. Set
`SECRET_KEY` (required) and, for persistent data, `DATABASE_URL` to a hosted
PostgreSQL database — the default SQLite store lives in `/tmp` and does not
persist across requests. See
[docs/SETUP.md](docs/SETUP.md#option-c--vercel-services) for the full guide.

---

## Using real models (optional)

The demo runs offline with deterministic stub adapters. To use hosted models,
set these in `.env` (never in frontend code):

```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
EMBEDDING_PROVIDER=openai
EMBEDDING_API_KEY=sk-...
```

The adapter layer (`backend/app/services/llm.py`, `embeddings.py`) means the
provider can be changed without touching the rest of the application.

---

## Tests

```bash
python -m pytest                  # full suite
python tests/run_validation.py    # 50-question validation harness
```

The validation harness prints measured metrics for the demo build. Those
numbers describe the **synthetic demo with stub models**, not real college
performance. See [docs/TESTING.md](docs/TESTING.md).

---

## Project layout

```text
campusmate/
├── frontend/            React + Vite app (pages, components, API client)
├── backend/             FastAPI app (routers, services, models, alembic)
│   ├── app/
│   │   ├── routers/     chat, documents, tickets, auth
│   │   └── services/    retrieval, answer policy, publishing, llm, embeddings
│   └── alembic/         database migrations
├── database/            PostgreSQL + pgvector schema
├── docs/                architecture, API, setup, testing, demo data, traceability
├── tests/               pytest suite + validation dataset
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── vercel.json          Vercel services (backend + frontend)
├── .env.example
└── README.md
```

---

## Planned (not implemented in this MVP)

Kept clearly separate from delivered features:

- Hindi and Marathi language support.
- Opt-in deadline reminders (would require explicit student consent).
- Student portal integration (requires authentication and a separate
  permission design).
- Staff review workflow for unanswered topics.

---

## Documentation index

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design and data flow
- [docs/API.md](docs/API.md) — API endpoints
- [docs/SETUP.md](docs/SETUP.md) — local and Docker setup
- [docs/TESTING.md](docs/TESTING.md) — test plan and measured results
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) — the 90-second demo sequence
- [docs/DEMO_DATA.md](docs/DEMO_DATA.md) — what the synthetic sample data is
- [docs/REQUIREMENTS_TRACEABILITY.md](docs/REQUIREMENTS_TRACEABILITY.md) — spec-to-code map

---

## Repository and deployment

This build is prepared for anonymous hackathon presentation. Replace the
placeholders below after publishing — do not invent URLs.

| Item | Value |
| --- | --- |
| GitHub repository | `https://github.com/<owner>/<repo>` (placeholder) |
| Deployed application | `https://<your-deployment-host>` (placeholder) |
| Demo login | Students self-register (public). Admin credentials come from the environment (`SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`) and are never published. |

Deployment notes: [docs/SETUP.md](docs/SETUP.md).

---

## Status and limitations

CampusMate is a hackathon-stage MVP. It is **not** claimed to be free of
hallucination or completely secure. It is an English-text demo that answers
from the approved documents loaded into it. Before real use it needs real
approved documents, a hosted model and embedding provider, production secrets,
HTTPS, and a review of the retention and access policies in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
