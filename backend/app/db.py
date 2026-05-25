from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL, SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD, SEED_ADMIN_ROLE

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

        # Seed default roles (INSERT OR IGNORE is idempotent)
        for _rname, _rdesc in [
            ("admin",     "Full administrative access"),
            ("moderator", "Content moderation rights"),
            ("user",      "Standard end user"),
        ]:
            conn.execute(
                text("INSERT OR IGNORE INTO roles (name, description) VALUES (:n, :d)"),
                {"n": _rname, "d": _rdesc},
            )

        # Seed default groups (INSERT OR IGNORE is idempotent)
        import datetime
        import uuid
        import bcrypt
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

        # Seed default admin user only when no admin-role user exists yet.
        # Skipped on every subsequent startup once any admin account is present.
        _existing_admin = conn.execute(
            text(
                "SELECT u.id FROM users u"
                " JOIN user_roles ur ON ur.user_id = u.id"
                " JOIN roles r      ON r.id = ur.role_id"
                " WHERE r.name = :role AND u.is_active = 1"
                " LIMIT 1"
            ),
            {"role": SEED_ADMIN_ROLE},
        ).fetchone()

        if not _existing_admin:
            _pw_hash = bcrypt.hashpw(
                SEED_ADMIN_PASSWORD.encode(), bcrypt.gensalt()
            ).decode()
            _new_id = str(uuid.uuid4())
            conn.execute(
                text(
                    "INSERT OR IGNORE INTO users"
                    "  (id, first_name, last_name, email, password_hash,"
                    "   email_verified, is_active, api_access, created_at, updated_at)"
                    " VALUES"
                    "  (:id, 'Admin', 'User', :email, :pw, 1, 1, 1, :ts, :ts)"
                ),
                {"id": _new_id, "email": SEED_ADMIN_EMAIL, "pw": _pw_hash, "ts": _ts},
            )
            _seed_user = conn.execute(
                text("SELECT id FROM users WHERE lower(email) = lower(:email)"),
                {"email": SEED_ADMIN_EMAIL},
            ).fetchone()
            _admin_role = conn.execute(
                text("SELECT id FROM roles WHERE name = :role"),
                {"role": SEED_ADMIN_ROLE},
            ).fetchone()
            if _seed_user and _admin_role:
                conn.execute(
                    text(
                        "INSERT OR IGNORE INTO user_roles (user_id, role_id, granted_at)"
                        " VALUES (:uid, :rid, :ts)"
                    ),
                    {"uid": _seed_user[0], "rid": _admin_role[0], "ts": _ts},
                )

        conn.commit()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a request-scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
