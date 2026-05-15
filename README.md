# CriteriaMeter

CriteriaMeter is a local-first web application for assessing software supply-chain security posture. It maps controls from two security frameworks — **SLSA v1.2** (Supply-chain Levels for Software Artifacts) and **OWASP ASVS 5.0** (Application Security Verification Standard) — across 8 shared security domains, and provides an interactive compliance checklist for tracking SLSA Build Track progress.

## Features

| Page | Description |
|------|-------------|
| **Meter Reading** | Interactive SLSA v1.2 Build Track checklist with per-level progress tracking (L1 → L2 → L3) |
| **Mapper** | Cross-framework control comparison — select SLSA v1.2, OWASP ASVS 5.0, or both to see how controls align across 8 security domains |
| **Dashboard** | Aggregated compliance overview (in development) |

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2
- **Frontend:** React 18, TypeScript, Vite, served by nginx in production
- **Storage:** Pre-computed JSON mapping (no database required for current features)

---

## Deployment

### Option 1 — Docker (recommended)

Both services have individual Dockerfiles. Build and run them in order.

**1. Build the images**

```bash
# From the project root
docker build -t criteriameter-backend ./backend
docker build -t criteriameter-frontend ./frontend
```

**2. Create a shared network**

```bash
docker network create criteriameter
```

**3. Run the backend**

```bash
docker run -d \
  --name criteriameter-backend \
  --network criteriameter \
  -p 8000:8000 \
  -v "$(pwd)/dataset:/dataset:ro" \
  -e CRITERIAMETER_ALLOWED_ORIGINS=http://localhost:3000 \
  criteriameter-backend
```

> The `dataset/` volume mount is required — the backend reads compliance data from it at startup.

**4. Run the frontend**

```bash
docker run -d \
  --name criteriameter-frontend \
  --network criteriameter \
  -p 3000:3000 \
  criteriameter-frontend
```

**5. Access in the browser**

| Service | URL |
|---------|-----|
| Frontend (React app) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API health check | http://localhost:8000/health |
| API docs (Swagger) | http://localhost:8000/docs |

---

### Option 2 — Local development (no Docker)

Prerequisites: Python 3.12+, Node 20+

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# Runs at http://localhost:8000
```

**Frontend** (in a separate terminal)

```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:3000
```

The Vite dev server automatically proxies all `/api/*` requests to `http://localhost:8000`, so no CORS configuration is needed during local development.

**Access in the browser**

Open http://localhost:3000 — the full application is available at this single address.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRITERIAMETER_ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated list of allowed CORS origins |

---

## Regenerating the control mapping

The cross-framework mapping is pre-computed and committed at `backend/app/mapping/output/unified_mapping.json`. Re-run the generator after changing datasets or domain assignments:

```bash
cd backend
source .venv/bin/activate
python -m app.mapping.run_mapping
```

Edit `backend/app/mapping/domains.py` to change how controls are assigned to domains without touching loader or mapper logic.
