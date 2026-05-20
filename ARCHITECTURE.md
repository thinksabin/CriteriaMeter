# CriteriaMeter — Lean Architecture

## Architectural Principle

Start with the smallest stack that can prove the core workflow. Add complexity
only after a measured bottleneck or a missing product need appears.

## V1 Stack

### Frontend

- React
- TypeScript

### Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x


### Storage

- SQLite
- In Memory database for the initial development without the storage

### Local Development

- API and frontend can run directly on the host for faster iteration

## Why This Is Enough

This stack supports the full V1 loop without introducing distributed-system
overhead:

- Upload files
- Parse and validate features
- 

## Explicitly Deferred

These can be added later if evidence justifies them:

- GraphQL
- Celery
- Redis
- DuckDB

## System Shape

```
    [React]
        |
     [FastAPI]
        |
    [SQLite]
        |
   [React Dashboard]
```

## API Direction

Use REST for V1. Keep it boring.

Suggested endpoints:

- `POST /datasets` to upload a dataset
- `GET /datasets` to list datasets
- `GET /datasets/{id}` to fetch dataset metadata and validation summary
- `GET /datasets/{id}/features` to fetch features in the current viewport or by
  filter
- `GET /datasets/{id}/features/{feature_id}` to inspect one feature

If GraphQL becomes useful later, add it after the object model and frontend
needs are stable.

## Data Access Strategy

- 

## Performance Strategy For V1

Do not design around speculative 10K-user load before a working product exists.

Start with:

- Bounding-box queries
- Pagination or feature limits
- Server-side filtering

Then measure.

## Upgrade Triggers

Only add more infrastructure when one of these happens:

- Request latency is consistently unacceptable under real usage
- Upload or processing tasks block the API long enough to hurt the product
- Large dataset rendering cannot be solved with query limits and simplification
- Deployment traffic requires connection pooling or edge caching

## Security Architecture

The [threat model](docs/threat-model/THREAT-MODEL-REPORT.md) was written against
the full architecture. With the lean V1 scope many components (GraphQL, Celery,
Redis, Martin, DuckDB, CDN, PgBouncer) are deferred, so the threats targeting
those components are also deferred. The threats below apply to the V1 stack.

### Authentication And Authorization

V1 is a single-user, local-first application. There is no multi-user
authentication or authorization in V1. Before any networked or multi-user
deployment, OAuth2/OIDC and dataset-level ownership must be designed and
implemented (threat model CT-01, CT-02).

### Trust Boundaries

```
[Browser]  ──  untrusted  ──>  [FastAPI]  ──  trusted  ──>  [SQLite]
                                   
```

All data crossing the browser-to-API boundary is untrusted: uploaded files,
query parameters, and request bodies. The API is the sole enforcement point.


### API Hardening

- **Rate limiting** — per-IP request rate limits on all endpoints (60/min
  default, 10/min on upload)
- **CORS** — restrict allowed origins to the frontend origin, configurable via
  `CRITERIAMETER_ALLOWED_ORIGINS` (CT-16) — **Implemented**
- **Security headers** — Content-Security-Policy, X-Content-Type-Options,
  X-Frame-Options, Strict-Transport-Security, Referrer-Policy,
  Permissions-Policy, Cache-Control (CT-16) — **Implemented**
  (`SecurityHeadersMiddleware`)
- **Request ID tracking** — unique UUID per request, propagated in
  `X-Request-ID` response header for log correlation — **Implemented**
  (`RequestIDMiddleware`)
- **Structured error responses** — never expose internal paths, stack traces,
  or database details to clients

### Database Security

- **Parameterized queries only** — via SQLAlchemy ORM; never interpolate user
  input into SQL — **Implemented**

### Output Encoding And XSS Prevention

- Never use `dangerouslySetInnerHTML`
- Sanitize or encode properties before rendering in DOM attributes
- Rely on React JSX auto-escaping as a baseline, not as the only defense
  (CT-14)

### Audit Logging

Log security-relevant events in structured JSON format: upload attempts,
ingestion results, validation failures, and any rejected requests. Include
request metadata (IP, user-agent, request ID) but never log credentials, PII,
or internal file paths (CT-15)

### Dependency Management

- Audit all third-party packages for known CVEs before adoption
- Enable automated dependency scanning (pip-audit, npm audit) in CI (CT-25)

### Deferred Security Work

These controls become necessary when the corresponding infrastructure is added:

- Redis AUTH and TLS (when Redis is introduced)
- Celery JSON serialization and message signing (when Celery is introduced)
- Martin layer restrictions and read-only DB user (when Martin is introduced)
- Inter-service TLS and per-service DB credentials (when the system becomes
  multi-service)
- Encryption at rest (before handling regulated data)

## First Build Checklist

- One backend service
- One frontend app
- In Memory database to create chart and dashboard
- End-to-end ingestion and visualization test

## Dashboard

- Heatmap per compliance items mentioned in dataset/reference.md