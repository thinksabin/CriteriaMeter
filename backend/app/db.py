from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL

_engine_kwargs: dict = {}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def run_migrations() -> None:
    """Idempotent column migrations and data seeds — safe to run on every startup."""
    with engine.connect() as conn:
        # api_access was added after initial schema creation
        existing_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if "api_access" not in existing_cols:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN api_access INTEGER NOT NULL DEFAULT 1"
            ))

        # Seed default groups (INSERT OR IGNORE is idempotent)
        import datetime
        _ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        for _name, _desc in [
            ("administrators", "Platform administrators"),
            ("staff",          "Internal staff members"),
            ("apiclients",     "Service accounts with API access"),
        ]:
            conn.execute(
                text(
                    "INSERT OR IGNORE INTO groups (name, description, created_at, updated_at)"
                    " VALUES (:n, :d, :ca, :ua)"
                ),
                {"n": _name, "d": _desc, "ca": _ts, "ua": _ts},
            )

        # Seed default auth settings (INSERT OR IGNORE is idempotent)
        for _key, _val in {
            "auth.signup_enabled":       "true",
            "auth.min_password_length":  "8",
            "auth.require_number":       "false",
            "auth.require_uppercase":    "false",
            "auth.require_special_char": "false",
        }.items():
            conn.execute(
                text("INSERT OR IGNORE INTO app_settings (key, value) VALUES (:k, :v)"),
                {"k": _key, "v": _val},
            )

        conn.commit()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a request-scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
