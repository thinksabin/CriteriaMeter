# CriteriaMeter

CriteriaMeter is a local-first web application for assessing software supply-chain security and compliance posture. It maps controls from five security frameworks across 18 shared domains and provides interactive checklists for tracking progress.

## Frameworks

| Framework | Type | Controls |
|-----------|------|----------|
| **SLSA v1.2** (Supply-chain Levels for Software Artifacts) | Supply-chain security | 26 |
| **OWASP ASVS 5.0** (Application Security Verification Standard) | Application security | 208 |
| **SOC 2** (AICPA Trust Services Criteria) | Compliance | 51 |
| **GDPR** (EU General Data Protection Regulation) | Compliance | 46 |
| **ISO 27001:2022** (Information Security Management) | Compliance | 116 |

## Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Heat-map overview of control coverage across all frameworks and domains |
| **Meter Reading › Supply Chain** | Interactive SLSA v1.2 Build Track checklist with per-level progress tracking (L1 → L2 → L3) |
| **Meter Reading › Compliance** | Live API-backed checklist for SOC 2, GDPR, and ISO 27001:2022 controls with per-framework progress |
| **Mapper › Supply Chain** | Cross-framework side-by-side comparison of SLSA v1.2 and OWASP ASVS 5.0 controls by domain |
| **Mapper › Compliance** | Cross-framework side-by-side comparison of SOC 2, GDPR, and ISO 27001:2022 controls by domain |

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x
- **Frontend:** React 18, TypeScript, Vite, served by nginx in production
- **Storage:** SQLite (local default) or PostgreSQL (production); pre-computed JSON mapping for control data

---

## Quickstart (local development)

The `dev.sh` script handles environment setup, dependency installation, and starts both servers.

```bash
chmod +x dev.sh
./dev.sh
```

Pass `--remap` to regenerate the unified control mapping before starting:

```bash
./dev.sh --remap
```

Open http://localhost:3000 once both servers are ready.

To stop both servers:

```bash
pkill -f uvicorn; pkill -f vite
```

---

## Manual local development

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

---

## Docker deployment

Both services have individual Dockerfiles.

**1. Build the images**

```bash
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
  -v "$(pwd)/backend:/data" \
  -e CRITERIAMETER_ALLOWED_ORIGINS=http://localhost:3000 \
  -e CRITERIAMETER_DATABASE_URL=sqlite:////data/criteriameter.db \
  criteriameter-backend
```

> The `dataset/` volume mount is required — the backend reads compliance data from it at startup.
> The `/data` volume persists the SQLite database file across container restarts. For production, set `CRITERIAMETER_DATABASE_URL` to a PostgreSQL connection string instead.

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
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Health check | http://localhost:8000/health |
| API docs (Swagger) | http://localhost:8000/docs |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRITERIAMETER_ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated list of allowed CORS origins |
| `CRITERIAMETER_DATABASE_URL` | `sqlite:///./criteriameter.db` | SQLAlchemy database URL. Use `postgresql://user:pass@host:5432/dbname` for PostgreSQL |

---

## Dataset files

Reference files and compliance datasets live under `dataset/` at the project root. The backend reads these at startup; mount the directory as a read-only volume in Docker.

| File | Description |
|------|-------------|
| `checklist_SLSAv1.2.txt` | SLSA v1.2 Build Track checklist (plain text) |
| `OWASP_Application_Security_Verification_Standard_5.0.0_en.csv` | OWASP ASVS 5.0 requirements |
| `soc2_checklist.csv` | SOC 2 Trust Services Criteria |
| `gdpr_checklist.csv` | GDPR requirements |
| `iso27001_checklist.csv` | ISO 27001:2022 controls |
| `reference.md` | Links to upstream specs |

---

## Regenerating the control mapping

The cross-framework mapping is pre-computed and committed at `backend/app/mapping/output/unified_mapping.json`. Re-run the generator after changing datasets or domain assignments:

```bash
cd backend
source .venv/bin/activate
python -m app.mapping.run_mapping
```

Edit `backend/app/mapping/domains.py` to change how controls are assigned to domains without touching loader or mapper logic.

The 18 control domains span two groups:

**Technical** — `build_process_integrity`, `provenance_and_traceability`, `cryptography_and_signing`, `secret_management`, `build_isolation`, `dependency_management`, `access_control_and_authorization`, `audit_logging`

**Compliance** — `comp_governance`, `comp_risk`, `comp_access_control`, `comp_data_protection`, `comp_security_ops`, `comp_physical`, `comp_vendor`, `comp_incident`, `comp_audit`, `comp_continuity`
