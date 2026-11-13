# AGENTS.md — CampusMate repository notes

Smart Student Helpdesk Chatbot. React + Vite frontend, FastAPI backend,
PostgreSQL + pgvector (SQLite fallback for zero-setup local dev). Ships with
the reviewed JSCOE website pack by default (`CAMPUSMATE_DATASET=jscoe`).
Synthetic data remains available through `CAMPUSMATE_DATASET=demo` for regression tests.

## JSCOE data maintenance

- Canonical FAQs/provenance: `backend/app/data/jscoe_knowledge.json`.
- After review, run `python scripts/sync_jscoe_data.py` to update the frontend snapshot.
- Startup imports stable document IDs once, retires tagged synthetic fixtures,
  and retains accounts, tickets, staff notices and staff retirements.
- Explicit refresh: from `backend`, run `python ../scripts/import_jscoe.py --refresh`.
- Never infer text from scanned documents without visual verification. Keep the
  original URL, actual format and checked date; do not call a checked date a
  publication date. The calendar has an exam window, not subject-wise times.
- Existing test fixtures and the 50-question harness explicitly select `demo`.
  Real-source regressions are in `tests/test_jscoe.py` and `frontend/tests`.

## Layout

- `frontend/` — React app (`src/pages`, `src/components`, `src/lib/api.js`).
  API client falls back to `src/lib/offlineEngine.js` when the backend is
  unreachable (surfaced as `mode: "live" | "offline"`).
- `backend/app/` — FastAPI app. `routers/` (HTTP), `services/` (logic),
  `models.py`, `schemas.py`, `security.py`, `config.py`.
- `backend/alembic/` — migrations. `database/schema.sql` — PostgreSQL reference.
- `tests/` — pytest suite + `dataset/questions.json` (50 questions) and
  `run_validation.py`.
- `docs/` — architecture, API, setup, testing, demo script, demo data,
  requirements traceability.

## Common commands

```bash
# backend (from backend/)
uvicorn app.main:app --reload --port 8000      # http://localhost:8000/docs
# frontend (from frontend/)
npm run dev                                     # http://localhost:5173
# tests (from repo root)
python -m pytest                                # 205 tests
python tests/run_validation.py                  # 50-question validation
# docker (from repo root)
cp .env.example .env && docker compose up --build   # :8080 frontend, :8000 api
# vercel services (from repo root)
vercel dev                                          # runs backend + frontend locally
```

**Accounts**: students self-register (public sign-up/sign-in); the chatbot,
noticeboard and tickets require a signed-in student. Admin (staff) accounts are
provisioned from the environment — there is no public admin sign-up and no
credentials are shown or pre-filled in the UI. Set `SEED_ADMIN_EMAIL` /
`SEED_ADMIN_PASSWORD` (and a strong `SECRET_KEY`) in the environment; the demo
admin password defaults to empty so no secret lives in the repo.

## Key conventions

- **GitHub upload**: target `ashokbon8/campusmate`, not the upstream repository.
  The current connected app rejected code writes with HTTP 403. Do not claim a
  push succeeded. `UPLOAD_TO_GITHUB.cmd` uses the user's local Git sign-in and
  `scripts/release_files.json` to upload only the release. The helper clones the
  existing main branch, preserves history, pushes without force and verifies
  the remote head. Never include private `.env`, databases or uploads.

- **Cloud hosting**: root `Dockerfile` builds React and serves it alongside
  FastAPI. `scripts/serve_cloud.py` obeys `PORT`; `app/cloud.py` requires hosted
  PostgreSQL and private admin/signing settings. `render.yaml` declares free
  web/database instances. Free Render PostgreSQL expires after 30 days; disclose
  this when discussing hackathon hosting. Do not claim an example URL is live.
- **Uploaded sources**: `document_files` stores original PDF bytes in the
  database so cloud restarts do not lose downloads or prevent re-indexing.
  Draft access checks must run before either local-file or database-file reads.
  Missing legacy originals can still use the indexed-text PDF fallback.

- **Final local ZIP**: `RUN_CAMPUSMATE.cmd` prepares Python and invokes one-time
  admin setup automatically. `app/local.py` mounts the API at `/api` and the
  built `frontend/dist` at `/`; `scripts/run_local.py` starts one server on 5173.
  The release ZIP must include `frontend/dist` alongside the full source.
  Node.js is needed for React development/building, not for running that ZIP.
  Package with files directly at ZIP root so the VS Code workspace opens the
  correct directory without a second nested project folder.

- **Exams**: `services/exam_rules.py` parses subject/semester wording;
  `services/exams.py` answers structured admin timetables before calendar help.
  `doc_type=exam` stores a complete JSON timetable in an indexed passage; keep
  it out of generic lexical retrieval. Admin writes require publisher access.
- **Example dates**: `backend/app/data/exam_data.json` contains official subject
  names/codes plus explicitly invented demo dates. Demo replies require
  `context.exam_data_mode=demo` and carry `is_sample_data=true`. Never merge
  example dates into the college knowledge pack. Run the existing data sync
  script after reviewing changes to keep the frontend and demo source page in sync.
- **Update installer**: code-only manifest; keep `.env`, databases and uploads
  untouched. Tests cover backups and private-file rejection.

- **Config is env-driven** (`app/config.py`, `.env.example`). Never hardcode
  secrets or put API keys in the frontend.
- **Brand colours**: midnight black `#080A0B`, pure white `#FFFFFF`, lime green
  `#C6FF00`. `frontend/src/brand.css` owns the final tokens and readable overrides.
- **Admin login**: public navigation opens the admin sign-in form; dashboard
  controls wait for `/auth/me`. Local credentials are chosen through
  `SETUP_ADMIN.cmd` and saved privately in `backend/.env`.
- **Account isolation**: staff and student JWT roles are checked in addition to
  account identity, even when both account types share an email address.
- **Model adapters**: `services/llm.py` and `services/embeddings.py` each have a
  deterministic offline implementation (`stub` / `hashing`) and a hosted one
  (`openai`). Tests and the demo use the offline ones.
- **Answer policy** (`services/answer_policy.py`, `services/chat.py`): three
  states — `answered`, `needs_context`, `escalated`. Answers must be grounded in
  retrieved evidence; never invent facts. Unsupported → escalate.
- **Embedding column is portable**: pgvector `Vector` on PostgreSQL, JSON text
  on SQLite (`models.py`). `cosine()` must accept both lists and numpy arrays —
  never call `bool()` on an embedding.
- **Synthetic data discipline**: every seeded notice is tagged `[SAMPLE DEMO
  DATA]` and titled `(sample)`; the UI shows a SAMPLE DATA tag and
  `is_sample_data: true`. Do not present sample data as real college info.
- **Proposed vs measured**: presentation targets live in the UI as *proposed*;
  measured demo numbers are separate (`docs/TESTING.md`). Never present targets
  as achieved results.

## Verified state

- `python -m pytest` → 205 passed, including local startup, cloud configuration
  guards, and original PDF download/re-index after local files are deleted.
- Upload tests use a local bare Git repository and check history preservation,
  private-file exclusion and rejecting unsafe release manifests. The Windows
  launcher and real GitHub write were not executed here.
- `cd frontend && npm test` → 55 passed; `npm run build` passes.
- Browser automation for this change could not run because the execution
  runtime disallows Chromium's Unix socket. Do not report browser QA as passed.
- React server rendering checked the header, admin login, homepage, timetable
  editor and chat exam-source controls.
- The new Render Docker image and a live deployment have not been run in this
  environment; the manifest and combined application routes have been checked.
- Validation harness → 25/25 supported answers, 100% citation coverage, 0
  unsupported guesses (demo build, stub models).
- Full `docker compose` stack (PostgreSQL + pgvector) verified end-to-end:
  health, chat with citation, frontend nginx `/api` proxy.
- Browser flows verified: clarification (progressive), answered-with-citation,
  escalation with ticket option.

## Gotchas

- `docker compose` backend may fail on first start if the `db` DNS name is not
  resolvable yet; `restart: unless-stopped` is set. In restricted sandboxes
  Docker's embedded DNS can fail entirely — verify the pgvector path by pointing
  `DATABASE_URL` at the published `127.0.0.1:5432` port instead.
- Auth routes are under the `/auth` prefix (`/auth/login`, `/auth/token`,
  `/auth/me`).
- Frontend `VITE_API_TARGET` (dev) / nginx `proxy_pass` (prod) must point at the
  backend for `/api` calls to work.
- Vercel services (`vercel.json`): `/api/(.*)` → `backend`, `/(.*)` →
  `frontend`. Vercel forwards the original path, so the app auto-sets
  `root_path=/api` when `VERCEL`/`VERCEL_ENV` is present; nginx (Docker) strips
  `/api` itself, so `root_path` stays empty there. `app.main:create_app(root_path=...)`
  builds the app for tests.
- Vercel's filesystem is read-only except `/tmp`, so the config falls back to
  `/tmp` for the SQLite DB and uploads when on Vercel (or when the cwd is not
  writable). That store is ephemeral — set `DATABASE_URL` to hosted PostgreSQL
  for persistence. Missing source files are regenerated from stored passages.
