# Setup

For the final Windows ZIP use [START_HERE.md](../START_HERE.md). For GitHub
submission and the single-service Render deployment use
[PUBLISH_ONLINE.md](../PUBLISH_ONLINE.md); it includes free-plan expiry limits.

Two ways to run CampusMate: a zero-setup local run (SQLite + offline stub
models) or the full stack with Docker (PostgreSQL + pgvector).

## Prerequisites

- **Local run:** Python 3.11+, Node.js 18+
- **Docker run:** Docker Engine with the Compose plugin

---

## Option A — Local run (recommended for a quick demo)

No database server or API key required. The backend defaults to SQLite and
deterministic offline model adapters.

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
# Frontend (second terminal)
cd frontend
npm install
npm run dev
```

- Frontend: <http://localhost:5173>
- API docs: <http://localhost:8000/docs>

The first backend start seeds synthetic sample notices. The Vite dev server
proxies `/api` to the backend.

### Accounts

**Students** create their own account from the public **Create account** page,
then sign in to reach the chatbot, noticeboard and helpdesk tickets. Account
details (name, email, hashed password, optional programme/semester) are stored
in the `students` table.

**Admin (staff)** accounts are provisioned from the environment — there is no
public admin sign-up and no credentials are shown in the UI. The demo admin is
created on first start from:

```
SEED_ADMIN_EMAIL     # e.g. admin@your-college.example
SEED_ADMIN_PASSWORD  # leave empty to skip creating a demo admin
SEED_ADMIN_NAME
```

Set these (plus a strong `SECRET_KEY`) in your environment or hosting provider;
never commit them to the repository.

---

## Option B — Docker (PostgreSQL + pgvector)

```bash
cp .env.example .env        # edit values; never commit .env
docker compose up --build
```

- Frontend: <http://localhost:8080>
- API docs: <http://localhost:8000/docs>

Services:

| Service | Image | Purpose |
| --- | --- | --- |
| `db` | `pgvector/pgvector:pg16` | PostgreSQL with the pgvector extension |
| `backend` | built from `Dockerfile.backend` | FastAPI app |
| `frontend` | built from `Dockerfile.frontend` | Static build served by nginx, proxying `/api` |

Stop with `docker compose down`. Add `-v` to also delete volumes (data).

---

## Option C — Vercel (services)

The repository root `vercel.json` deploys the FastAPI backend and the Vite
frontend as two **services** in a single Vercel project, with shared routing on
one domain:

```json
{
  "services": {
    "backend": { "root": "backend", "framework": "fastapi", "entrypoint": "app.main:app" },
    "frontend": { "root": "frontend", "framework": "vite" }
  },
  "rewrites": [
    { "source": "/api/(.*)", "destination": { "service": "backend" } },
    { "source": "/(.*)", "destination": { "service": "frontend" } }
  ]
}
```

`/api/*` is routed to the backend; every other path goes to the frontend. Both
services are internal by default and only receive traffic through these
top-level rewrites, so the frontend and API share one Vercel domain.

The platform forwards the original path, so a request to `/api/chat` reaches the
backend as `/api/chat` (it is not stripped). The app detects a Vercel deployment
(`VERCEL` / `VERCEL_ENV`) and automatically sets `root_path` to `/api`, so its
routes match and the OpenAPI docs plus the citation `open_url` links stay
correct. No manual `ROOT_PATH` is needed on Vercel; set it explicitly only if you
mount the API somewhere other than `/api`.

### Storage on Vercel

Vercel Functions have a **read-only filesystem** with a writable `/tmp` scratch
space, and the working directory is not writable. When the app detects Vercel (or
a non-writable working directory) its writable defaults move to `/tmp`, so it
boots and the seeded demo works out of the box:

| Setting | Local / Docker default | Vercel default |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./campusmate.db` | `sqlite:////tmp/campusmate.db` |
| `UPLOAD_DIR` | `./storage/documents` | `/tmp/campusmate-documents` |

**Persistence:** `/tmp` is per-instance and ephemeral, so on Vercel the default
SQLite database (and any uploaded source files) do **not** persist across
invocations — each cold instance re-seeds the synthetic sample data. The public
site, chat, citations and source viewer all work; admin edits and student
tickets may be lost between requests. This is fine for a demo but not for real
use.

**To persist data**, set `DATABASE_URL` to a hosted PostgreSQL database (for
example [Neon](https://neon.tech), which Vercel integrates with). The app creates
the `vector` extension and tables automatically on first start, and re-seeds the
included notices into it. New uploaded source PDFs are retained as original
bytes in the database, so source viewing and re-indexing survive temporary-file
loss. Legacy documents without that copy fall back to a PDF of indexed text.

Example connection string (use the pooled URL from your provider):

```
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

`postgres://` URLs (as some providers hand out) are normalised to
`postgresql://` automatically.

#### Using Supabase for persistence

Supabase is a hosted PostgreSQL provider that works here with no code changes —
the `students` table (and every other table) is created automatically on first
start. In the Supabase dashboard:

1. **Project → Settings → Database → Connection string** and copy the **URI**.
2. Prefer the **Connection pooling** URI (host `aws-0-<region>.pooler.supabase.com`,
   port `6543`) for serverless Vercel Functions. Replace the password
   placeholder with your database password.
3. Make sure the URL ends with `?sslmode=require`.
4. In Vercel set the environment variable (Settings → Environment Variables):

   ```
   DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres?sslmode=require
   ```

   Optionally also set `SECRET_KEY`, `SEED_ADMIN_EMAIL` and
   `SEED_ADMIN_PASSWORD` (private staff login). Then redeploy.

That single `DATABASE_URL` value is the only database secret you need to import
into Vercel — student sign-ups then persist in Supabase instead of the
ephemeral `/tmp` SQLite file. If the `vector` extension is not enabled, enable it
under **Database → Extensions** (pgvector); the app also runs without it using
the JSON embedding fallback.

### Required environment variables (Vercel)

Set these in **Project → Settings → Environment Variables**:

| Variable | Required? | Notes |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Long random string; signs admin **and student** JWTs. Do not use the default. |
| `DATABASE_URL` | For persistence | Hosted PostgreSQL (e.g. Supabase/Neon). Omit for the ephemeral `/tmp` demo. |
| `CAMPUSMATE_SEED` | Optional | `1` (default) seeds the sample notices; `0` starts empty. |
| `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD` | Recommended | Private staff login. No admin credentials are shown in the UI; set these in the environment so no secret lives in the repository. |
| `LLM_PROVIDER` / `LLM_API_KEY` | Optional | `openai` + key to use a hosted model; default offline `stub`. |
| `EMBEDDING_PROVIDER` / `EMBEDDING_API_KEY` | Optional | `openai` + key to use hosted embeddings; default `hashing`. |

Do not set `ROOT_PATH` unless you change the public prefix.

Run everything locally with `vercel dev` from the repository root.

---

## Configuration

All settings are environment variables (see `.env.example`). Key ones:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLite (default) or `postgresql+psycopg2://...` |
| `SECRET_KEY` | JWT signing key — **change in production** |
| `LLM_PROVIDER` | `stub` (offline) or `openai` |
| `LLM_API_KEY` | Hosted model key (server-side only) |
| `EMBEDDING_PROVIDER` | `hashing` (offline) or `openai` |
| `EMBEDDING_API_KEY` | Hosted embedding key |
| `RETRIEVAL_MIN_SCORE` / `RETRIEVAL_MIN_COVERAGE` | Evidence thresholds |
| `CAMPUSMATE_SEED` | `1` seeds demo data on start, `0` starts empty |
| `UPLOAD_DIR`, `MAX_UPLOAD_MB` | Where notices are stored and size limit |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `ROOT_PATH` | Public path prefix the API is served under (e.g. `/api` on Vercel); empty for local/Docker |

Never commit a real `.env`. `.gitignore` excludes it.

---

## Database migrations (Alembic)

The schema is created automatically on startup. For explicit migrations:

```bash
cd backend
# against your configured DATABASE_URL
alembic upgrade head

# create a new migration after model changes
alembic revision --autogenerate -m "describe change"
```

The PostgreSQL reference schema is also in `database/schema.sql`.

---

## Switching to hosted models

```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
EMBEDDING_PROVIDER=openai
EMBEDDING_API_KEY=sk-...
```

Restart the backend. Because embeddings change, re-index existing documents
(`POST /admin/notices/{id}/reindex`) so stored vectors match the new model.

---

## Running the tests

```bash
# from the repository root
python -m pytest
python tests/run_validation.py
```

See [TESTING.md](TESTING.md) for what each covers.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Frontend shows "Offline" badge | Backend not reachable; start it or check `VITE_API_TARGET` |
| `401 Not authenticated` | Log in again; token expired |
| `403 requires publisher permissions` | Account role is `viewer`; use an `admin`/`publisher` account |
| Port already in use | Change `--port` / compose port mapping |
| Empty chatbot after switching embedding provider | Re-index documents |
