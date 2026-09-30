# Work Intake System

A small internal tool for triaging incoming work items: items come in, get analysed by an LLM
(category, priority, summary, recommended action), get reviewed by a human, and get completed.

- **Backend**: Django 5 + Django REST Framework, PostgreSQL, pytest
- **Frontend**: React + TypeScript + Vite, Redux Toolkit / RTK Query
- **LLM provider**: Groq (OpenAI-compatible API), swappable via `LLM_PROVIDER`

See [docs/DECISIONS.md](docs/DECISIONS.md) for architecture decisions and [docs/AI_USAGE.md](docs/AI_USAGE.md)
for the AI usage log.

## Prerequisites

- Python 3.11+
- Node 20+
- Docker (for PostgreSQL) — or a local Postgres instance
- A Groq API key (or Gemini, see [Switching LLM provider](#switching-llm-provider))

## Setup

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

## Running tests

```bash
# backend
cd backend
python -m pytest

# frontend
cd frontend
npm run test
```

## Switching LLM provider

Set `LLM_PROVIDER` in `.env` to `gemini` or `groq`, and set `LLM_API_KEY` to a matching key for
that provider — the two settings must agree, since the key format differs per provider. See
`backend/work_items/ai/providers.py` for the provider implementations.

## API reference

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
curl -X POST https://your-backend.onrender.com/api/work-items/ \
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
curl -X POST https://<your-backend-url>/api/work-items/ \
  -H "Content-Type: application/json" \
  -d '{"externalId":"CRM-100","title":"Missing payslip","description":"Client has not uploaded latest payslip"}'
```

Both return `201 Created` for a new `externalId`, `200 OK` if the same
`externalId` and payload are sent again, or `409 Conflict` if the same
`externalId` arrives with a different payload.

## Deployment

- Frontend → Vercel
- Backend → Render
- Database → Neon
