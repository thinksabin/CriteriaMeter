import os
from pathlib import Path
from typing import Any

import yaml

# config.yml lives at the project root, two directories above this file
_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yml"


def _load_yaml() -> dict[str, Any]:
    try:
        with _CONFIG_PATH.open() as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


_cfg = _load_yaml()


def _yml(path: str, default: Any = None) -> Any:
    """Walk a dot-separated path through the loaded YAML config."""
    node: Any = _cfg
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node if node is not None else default


def _get(env_var: str, yml_path: str, default: Any) -> Any:
    """Priority: environment variable > config.yml > hardcoded default."""
    val = os.getenv(env_var)
    if val is not None:
        return val
    return _yml(yml_path, default)


# ── Database ───────────────────────────────────────────────────────────────────
DATABASE_URL: str = _get(
    "CRITERIAMETER_DATABASE_URL", "database.url", "sqlite:///./criteriameter.db"
)

# ── Auth / JWT ─────────────────────────────────────────────────────────────────
SECRET_KEY: str = _get(
    "CRITERIAMETER_SECRET_KEY", "auth.secret_key", "dev-secret-key-change-in-production"
)
JWT_ALGORITHM: str = str(_yml("auth.algorithm", "HS256"))
JWT_EXPIRE_MINUTES: int = int(_yml("auth.token_expire_minutes", 60))
COOKIE_SECURE: bool = str(
    _get("CRITERIAMETER_COOKIE_SECURE", "auth.cookie_secure", "false")
).lower() in ("1", "true", "yes")

# ── Server ─────────────────────────────────────────────────────────────────────
_raw_origins = _get(
    "CRITERIAMETER_ALLOWED_ORIGINS", "server.allowed_origins", "http://localhost:3000"
)
ALLOWED_ORIGINS: list[str] = (
    _raw_origins
    if isinstance(_raw_origins, list)
    else [o.strip() for o in str(_raw_origins).split(",")]
)

BACKEND_PORT: int = int(
    os.getenv("CRITERIAMETER_BACKEND_PORT") or str(_yml("server.backend_port", 8000))
)

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_LEVEL: str = str(
    _get("CRITERIAMETER_LOG_LEVEL", "app.log_level", "info")
).lower()

# ── Seed data ──────────────────────────────────────────────────────────────────
SEED_ADMIN_EMAIL: str = str(
    _get("CRITERIAMETER_SEED_ADMIN_EMAIL", "seed.admin_user.email", "admin@admin.com")
)
SEED_ADMIN_PASSWORD: str = str(
    _get("CRITERIAMETER_SEED_ADMIN_PASSWORD", "seed.admin_user.password", "admin123")
)
SEED_ADMIN_ROLE: str = str(
    _get("CRITERIAMETER_SEED_ADMIN_ROLE", "seed.admin_user.role", "admin")
)
