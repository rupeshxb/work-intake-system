# Work Intake System

A small internal tool for triaging incoming work items: items come in (from a CRM or the UI),
get analysed by an LLM (category, priority, summary, recommended action), get reviewed by a
human, and get completed.

## Live Demo

- **Frontend**: https://work-intake-system.vercel.app
- **Backend API**: https://work-intake-system.up.railway.app/api
- **Health check**: https://work-intake-system.up.railway.app/api/health/

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Key Engineering Decisions](#key-engineering-decisions)
- [Setup](#setup)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Simulating CRM Submissions](#simulating-crm-submissions)
- [Assumptions](#assumptions)
- [Production Considerations](#production-considerations)
- [AI-Assisted Development](#ai-assisted-development)

## Architecture Overview

An external CRM (or the frontend, via a demo form) submits work items to the backend, which
persists them, runs LLM analysis, and exposes the result for human review.

```
CRM  ──POST /api/work-items/──▶  Backend (Django + DRF + Postgres)  ──▶  LLM Provider (Groq)
                                          ▲
Frontend (React)  ─────────REST──────────┘
```

The backend is organized into layers — `domain/` (pure state-machine logic, no Django imports),
`services/` (business logic), `ai/` (LLM provider abstraction), `api/` (thin HTTP layer) — so that
each concern can change independently; see [docs/DECISIONS.md](docs/DECISIONS.md) for the reasoning.

## Tech Stack

| Area       | Technologies                                      |
| ---------- | -------------------------------------------------- |
| Backend    | Django, Django REST Framework, PostgreSQL, Pydantic |
| Frontend   | React, TypeScript, Redux Toolkit (RTK Query), Vite  |
| AI         | Groq (OpenAI-compatible API)                        |
| Deployment | Railway (backend), Vercel (frontend), Neon (database) |
| CI         | GitHub Actions                                      |

## Key Engineering Decisions

- **Idempotent intake with a concurrency test.** `POST /work-items/` is safe to call twice with
  the same `externalId` — it returns the existing row instead of erroring, and a dedicated test
  fires 10 concurrent requests with the same `externalId` to prove only one row is ever created.
  Why: this is exactly the failure mode a real CRM retry would hit. See
  [`backend/work_items/services/intake.py`](backend/work_items/services/intake.py) and
  [`backend/work_items/tests/test_intake.py`](backend/work_items/tests/test_intake.py).
- **Atomic state transitions.** Every status change goes through an explicit
  `ALLOWED_TRANSITIONS` map and a conditional DB update (`status__in=[...]`), so a work item can
  never skip a state or be double-processed by two concurrent requests. Why: the alternative —
  reading status then writing it — has a race window under concurrent access. See
  [`backend/work_items/domain/workflow.py`](backend/work_items/domain/workflow.py) and
  [`backend/work_items/services/analysis.py`](backend/work_items/services/analysis.py).
- **LLM reliability via Pydantic validation.** Every LLM response is validated against a strict
  Pydantic schema (enum category/priority, max-length strings) before being trusted; anything
  malformed is treated as a failed attempt, not a corrupted work item. Why: LLM output isn't
  guaranteed to match the requested schema even when asked for JSON. See
  [`backend/work_items/ai/schema.py`](backend/work_items/ai/schema.py).
- **LLM provider abstracted behind an interface.** `BaseAnalysisProvider` decouples business logic
  from any specific LLM vendor. Why: this was proven mid-project when Gemini's API broke and the
  swap to Groq only touched `providers.py` — see
  [AI-Assisted Development](#ai-assisted-development) and
  [`backend/work_items/ai/providers.py`](backend/work_items/ai/providers.py).

## Setup

### Prerequisites

- Python 3.11+
- Node 20+
- Docker (for PostgreSQL) — or a local Postgres instance
- A Groq API key (or Gemini, see [Switching LLM provider](#switching-llm-provider))

### Local development

1. Copy `.env.example` to `.env` at the project root and fill in real values (`DJANGO_SECRET_KEY`,
   `LLM_API_KEY`, etc).
2. Start Postgres:

   ```bash
   docker compose up -d
   ```

3. Backend:

   ```bash
   cd backend
   python -m venv .venv
   .venv/Scripts/activate   # or source .venv/bin/activate on macOS/Linux
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

   The API is served at `http://localhost:8000/api/`.

4. Frontend:

   ```bash
   cd frontend
   cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000/api
   npm install
   npm run dev
   ```

   The app is served at `http://localhost:5173`.

### Running the backend in Docker

As an alternative to the manual venv steps above (step 3), `docker compose` builds and runs the
backend and Postgres together, using `backend/Dockerfile`:

```bash
docker compose up --build
```

The API is served at `http://localhost:8000/api/`. To run the backend test suite inside the same
container setup:

```bash
docker compose run --rm backend pytest
```

### Switching LLM provider

Set `LLM_PROVIDER` in `.env` to `gemini` or `groq`, and set `LLM_API_KEY` to a matching key for
that provider — the two settings must agree, since the key format differs per provider. See
`backend/work_items/ai/providers.py` for the provider implementations.

### Deployment

- Frontend → Vercel
- Backend → Railway (built from [`backend/Dockerfile`](backend/Dockerfile) via
  [`railway.toml`](railway.toml))
- Database → Neon

On Railway, `railway.toml` points at `backend/Dockerfile` for the build and runs
`python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` on deploy.
Set `DJANGO_SECRET_KEY`, `DATABASE_URL` (your Neon connection string), `DJANGO_DEBUG=False`,
`ALLOWED_HOSTS` (your Railway domain, comma-separated with any custom domain),
`CORS_ALLOWED_ORIGINS` (your Vercel frontend URL), `LLM_PROVIDER`, and `LLM_API_KEY` as real
environment variables in the Railway service — these override the placeholder values baked into
the image for `collectstatic` at build time.

## Testing

```bash
# backend
cd backend
python -m pytest

# frontend
cd frontend
npm run test
```

The showcase test is
[`test_concurrent_duplicate_external_id_creates_one_row`](backend/work_items/tests/test_intake.py) —
it fires 10 threads at `POST /work-items/` with the same `externalId` simultaneously and asserts
exactly one row exists afterward, proving the idempotent-intake guarantee actually holds under
real concurrency (this needs real Postgres, not SQLite — see
[docs/DECISIONS.md](docs/DECISIONS.md) #001). Both suites also run automatically on every push and
pull request via [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## API Reference

| Method | Path                          | Description                                  |
| ------ | ----------------------------- | --------------------------------------------- |
| GET    | `/api/health/`                 | Health check                                   |
| GET    | `/api/work-items/`             | List work items (`?status=`, `?page=`)         |
| POST   | `/api/work-items/`             | Create a work item (idempotent on `externalId`)|
| GET    | `/api/work-items/:id/`         | Fetch a single work item                       |
| POST   | `/api/work-items/:id/analyse/` | Trigger LLM analysis                           |
| POST   | `/api/work-items/:id/retry/`   | Retry analysis for a failed item               |
| PATCH  | `/api/work-items/:id/status/`  | Move a reviewed item to `COMPLETED`            |

### Raw commands

These hit the API directly, without the UI — this is how an external system (e.g. a CRM) would
call it.

Create a work item:

```bash
curl -X POST https://work-intake-system.up.railway.app/api/work-items/ \
  -H "Content-Type: application/json" \
  -d '{"externalId":"CRM-100","title":"Missing payslip","description":"Client hasn'\''t uploaded latest payslip"}'
```

Locally, replace the host with `http://localhost:8000`:

```bash
curl -X POST http://localhost:8000/api/work-items/ \
  -H "Content-Type: application/json" \
  -d '{"externalId":"CRM-100","title":"Missing payslip","description":"Client hasn'\''t uploaded latest payslip"}'
```

Fetch it back:

```bash
curl http://localhost:8000/api/work-items/?status=RECEIVED
```

Trigger analysis:

```bash
curl -X POST http://localhost:8000/api/work-items/<id>/analyse/
```

Mark it complete once reviewed:

```bash
curl -X PATCH http://localhost:8000/api/work-items/<id>/status/ \
  -H "Content-Type: application/json" \
  -d '{"status":"COMPLETED"}'
```

## Simulating CRM Submissions

The `POST /work-items/` endpoint is designed to be called by an external
business system (a CRM), not by a human through a UI. Two ways to test it,
both producing identical results since they call the same endpoint:

### 1. Via the frontend (demo-friendly)
Open the app and expand **"Simulate CRM Submission"** above the work item
list. Fill in External ID, Title, and Description, then submit. This is a
thin form that builds the same JSON payload described below — it exists
only for demo convenience, not as a feature operations staff would use.

### 2. Via direct HTTP request (how the real CRM would call it)

**Local:**
```bash
curl -X POST http://localhost:8000/api/work-items/ \
  -H "Content-Type: application/json" \
  -d '{"externalId":"CRM-100","title":"Missing payslip","description":"Client has not uploaded latest payslip"}'
```

**Deployed:**
```bash
curl -X POST https://work-intake-system.up.railway.app/api/work-items/ \
  -H "Content-Type: application/json" \
  -d '{"externalId":"CRM-100","title":"Missing payslip","description":"Client has not uploaded latest payslip"}'
```

Both return `201 Created` for a new `externalId`, `200 OK` if the same
`externalId` and payload are sent again, or `409 Conflict` if the same
`externalId` arrives with a different payload.

## Assumptions

Pulled from [docs/DECISIONS.md](docs/DECISIONS.md):

- **Real Postgres is required, not just for production** — the concurrent-duplicate test needs
  real concurrent writes, and SQLite serializes writes, which would hide the exact race condition
  the test exists to catch (#001).
- **The domain layer has zero Django imports on purpose** — `domain/workflow.py` is assumed to
  need no database or environment variables to test, and to be reusable from a Celery worker or
  CLI later without pulling in the full Django stack (#004).
- **LLM provider choice is a swappable implementation detail, not a hard dependency** — the
  interface was designed assuming a provider could become unavailable or change breaking ways at
  any time (confirmed in practice: #005).

## Production Considerations

This is a scaffold-stage project. For real production use, the following would need to change:

- **Async analysis via Celery** — `AnalysisService.run()` currently calls the LLM synchronously
  inside the request/response cycle; a slow or hanging provider call would block a web worker.
- **Auth on endpoints** — there is currently no authentication or authorization on any
  `/api/work-items/*` endpoint; anyone who can reach the API can read or mutate work items.
- **Rate limiting** — nothing currently prevents a caller (or a runaway CRM retry loop) from
  flooding the intake endpoint or triggering repeated LLM calls.
- **Observability** — no structured logging, metrics, or error tracking (e.g. Sentry) currently
  exists; debugging a production failure means reading `AnalysisAttempt` rows by hand.
- **Database connection pooling** — Django's default per-request connection handling doesn't scale
  well under load; a pooler (e.g. PgBouncer, or Neon's built-in pooling) would be needed.

## AI-Assisted Development

See [docs/AI_USAGE.md](docs/AI_USAGE.md) for the full log. Summary:

- **Tool used**: Claude Code, for scaffolding and implementing individual layers (e.g. the
  domain state machine in `workflow.py` plus its parametrized tests) from explicit specs.
- **How it was verified**: generated code was read in full before running, then verified by
  running the actual test suite (e.g. 12/12 passing for the state machine step) and confirming
  constraints like "zero Django imports" by inspection, not by trusting the output.
- **A real example of something that changed mid-project**: the LLM provider was originally
  Gemini, chosen for its free tier. During development, Google AI Studio's newer API key format
  turned out to be broken against the standard REST API (a platform-wide issue, not
  account-specific). The provider was switched to Groq instead. Because the provider was already
  abstracted behind `BaseAnalysisProvider`, the swap only touched `providers.py` —
  `AnalysisService` and all existing tests were unaffected. See
  [docs/DECISIONS.md](docs/DECISIONS.md) #005.
