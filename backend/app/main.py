import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.mapping import router as mapping_router
from app.config import ALLOWED_ORIGINS
from app.db import Base, engine, run_migrations
import app.models  # noqa: F401 — registers ORM models with Base before create_all

Base.metadata.create_all(bind=engine)
run_migrations()

app = FastAPI(title="CriteriaMeter API", version="0.1.0")
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(mapping_router)

# CORS — origins sourced from config.yml / CRITERIAMETER_ALLOWED_ORIGINS env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Cache-Control"] = "no-store"
    return response


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")
