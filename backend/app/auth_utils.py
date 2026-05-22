"""
Shared helpers for auth settings and password validation.
Imported by both app.api.auth and app.api.admin.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.settings import AppSetting

_SPECIAL_CHARS = set(r'!@#$%^&*()_+-=[]{}|;:\'",.<>?/`~\\')

_DEFAULTS: dict[str, str] = {
    "auth.signup_enabled":      "true",
    "auth.min_password_length": "8",
    "auth.require_number":      "false",
    "auth.require_uppercase":   "false",
    "auth.require_special_char":"false",
}


@dataclass
class AuthSettings:
    signup_enabled:      bool
    min_password_length: int
    require_number:      bool
    require_uppercase:   bool
    require_special_char: bool


def get_auth_settings(db: Session) -> AuthSettings:
    def _val(key: str) -> str:
        row = db.get(AppSetting, key)
        return row.value if row else _DEFAULTS[key]

    return AuthSettings(
        signup_enabled      = _val("auth.signup_enabled")       == "true",
        min_password_length = int(_val("auth.min_password_length")),
        require_number      = _val("auth.require_number")        == "true",
        require_uppercase   = _val("auth.require_uppercase")     == "true",
        require_special_char= _val("auth.require_special_char")  == "true",
    )


def validate_password(password: str, settings: AuthSettings) -> str | None:
    """Return an error message string, or None if the password is valid."""
    if len(password) < settings.min_password_length:
        return f"Password must be at least {settings.min_password_length} characters."
    if settings.require_number and not any(c.isdigit() for c in password):
        return "Password must contain at least one number."
    if settings.require_uppercase and not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if settings.require_special_char and not any(c in _SPECIAL_CHARS for c in password):
        return "Password must contain at least one special character."
    return None
