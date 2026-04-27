# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

**Backend:** Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite — lives in `backend/`
**Frontend:** React 18, TypeScript, Vite, React Router v6 — lives in `frontend/`
**Containers:** each service has its own `Dockerfile`; `docker-compose.yml` wires them together

## Commands

```bash
# Run both containers
docker compose up --build

# Backend (local)
cd backend && uvicorn app.main:app --reload   # http://localhost:8000
pytest
ruff check . && mypy .

# Frontend (local)
cd frontend && npm install && npm run dev     # http://localhost:3000
npm run build
npm run lint
```

## Architecture

```
[React (TypeScript)]
        | REST
   [FastAPI]
        | SQLAlchemy ORM
    [SQLite]
```

The API is the sole trust boundary. All browser input (files, query params, request bodies) is untrusted; SQLite is trusted.

### REST Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/datasets` | Upload a dataset |
| `GET` | `/datasets` | List datasets |
| `GET` | `/datasets/{id}` | Metadata + validation summary |
| `GET` | `/datasets/{id}/features` | Paginated/filtered features |
| `GET` | `/datasets/{id}/features/{feature_id}` | Single feature |

### Architectural Rules

- **No speculative infra.** GraphQL, Celery, Redis, and DuckDB are explicitly deferred. Add only when a concrete bottleneck or product need appears (see upgrade triggers in `ARCHITECTURE.md`).
- **ORM only** — never interpolate user input into raw SQL.
- **Config via env vars** — all secrets/config through `CRITERIAMETER_*` environment variables.
- **Raw uploads stored outside the web root** — never served by the frontend.

### Required Backend Middleware

- `SecurityHeadersMiddleware` — CSP, X-Content-Type-Options, X-Frame-Options, HSTS, Referrer-Policy, Permissions-Policy, Cache-Control
- `RequestIDMiddleware` — UUID per request, echoed in `X-Request-ID` response header
- Rate limiting — 60 req/min default, 10 req/min on upload endpoints
- CORS — frontend origin only, configured via `CRITERIAMETER_ALLOWED_ORIGINS`

### Frontend XSS Constraint

Feature properties sourced from uploaded datasets are untrusted. Never use `dangerouslySetInnerHTML`. JSX auto-escaping is a baseline, not the sole defense.

### Structured Logging

Log upload attempts, ingestion results, validation failures, and rejected requests as structured JSON. Include request ID, IP, and user-agent. Never log credentials, PII, or internal file paths.

## First Build Checklist

- [x] Backend service (FastAPI) — `backend/app/main.py`, health endpoint at `GET /health`
- [x] Frontend app (React + TypeScript) — Home, Dashboard, About pages with left-nav shell
- [ ] End-to-end ingestion and visualization test

## Dataset directory

Reference files and compliance datasets live at the **project root** in `dataset/` (not inside `frontend/` or `backend/`). Current contents:

- `reference.md` — links to external specs (e.g. SLSA v1.2)
- `checklist_SLSAv1.2.txt` — static plain-text SLSA v1.2 checklist
- `OWASP_Application_Security_Verification_Standard_5.0.0_en.csv` — OWASP ASVS 5.0 source data

The backend reads from this directory; mount it into the backend container as a read-only volume.

## Unified control model

- Framework-mapping code lives in `backend/app/mapping/`
- Analysis code (dashboard data, aggregation) lives in `backend/app/analysis/`
- Generated output: `backend/app/mapping/output/unified_mapping.json`

To regenerate the mapping after dataset or domain changes:
```bash
cd backend
python -m app.mapping.run_mapping   # requires pydantic; use .venv if needed
```

Mapping is organised around 8 control domains that span both frameworks:
`build_process_integrity`, `provenance_and_traceability`, `cryptography_and_signing`,
`secret_management`, `build_isolation`, `dependency_management`,
`access_control_and_authorization`, `audit_logging`.

Domain assignments live in `backend/app/mapping/domains.py` — edit there to tune mappings
without touching loader or mapper logic.

## UI Dashboard

- Heat map per security framework and dataset
