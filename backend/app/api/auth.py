import datetime
import json
import uuid

import bcrypt
import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth_utils import get_auth_settings, validate_password
from app.config import COOKIE_SECURE, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, SECRET_KEY
from app.db import get_db
from app.dependencies import _load_user_with_roles, effective_role_names, get_current_user
from app.models.user import AuditLog, User, UserSession

router = APIRouter(prefix="/api/auth", tags=["auth"])

_COOKIE_NAME = "cm_token"
_COOKIE_PATH = "/"


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── Schemas ───────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    mobile_number: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v

    @field_validator("password")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v:
            raise ValueError("must not be empty")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    roles: list[str] = []


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _make_token(user_id: str) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=JWT_ALGORITHM)


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
        max_age=JWT_EXPIRE_MINUTES * 60,
        path=_COOKIE_PATH,
    )
    # Readable presence flag — lets the frontend skip the /me call when clearly not logged in.
    # Not HttpOnly intentionally; carries no secret value.
    response.set_cookie(
        key="cm_present",
        value="1",
        httponly=False,
        secure=COOKIE_SECURE,
        samesite="strict",
        max_age=JWT_EXPIRE_MINUTES * 60,
        path=_COOKIE_PATH,
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
        path=_COOKIE_PATH,
    )
    response.delete_cookie(
        key="cm_present",
        httponly=False,
        secure=COOKIE_SECURE,
        samesite="strict",
        path=_COOKIE_PATH,
    )


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        roles=sorted(effective_role_names(user)),
    )


def _audit(db: Session, action: str, actor_id: str | None = None,
           target_id: str | None = None, meta: dict | None = None) -> None:
    db.add(AuditLog(
        actor_id=actor_id,
        action=action,
        target_id=target_id,
        meta=json.dumps(meta) if meta else None,
        created_at=_now(),
    ))


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: Session = Depends(get_db)) -> UserOut:
    settings = get_auth_settings(db)

    if not settings.signup_enabled:
        raise HTTPException(status_code=403, detail="User registration is currently disabled.")

    if db.query(User).filter(func.lower(User.email) == body.email.strip().lower()).first():
        raise HTTPException(status_code=409, detail="Email already registered.")

    pw_error = validate_password(body.password, settings)
    if pw_error:
        raise HTTPException(status_code=422, detail=pw_error)

    user = User(
        id=str(uuid.uuid4()),
        first_name=body.first_name.strip(),
        last_name=body.last_name.strip(),
        email=body.email.strip(),
        mobile_number=body.mobile_number,
        password_hash=_hash_password(body.password),
        email_verified=0,
        is_active=1,
        created_at=_now(),
        updated_at=_now(),
    )
    db.add(user)
    _audit(db, action="user.create", target_id=user.id)
    db.commit()
    db.refresh(user)
    # New users have no roles yet — return empty list
    return UserOut(id=user.id, email=user.email,
                   first_name=user.first_name, last_name=user.last_name)


@router.post("/login", response_model=UserOut)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)) -> UserOut:
    user = db.query(User).filter(
        func.lower(User.email) == body.email.strip().lower()
    ).first()

    if not user or not _verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")

    user.last_login_at = _now()
    _audit(db, action="user.login", actor_id=user.id, target_id=user.id)
    db.commit()

    _set_session_cookie(response, _make_token(user.id))

    # Re-fetch with roles for the response payload
    full_user = _load_user_with_roles(db, user.id)
    if not full_user:
        raise HTTPException(status_code=500, detail="Session error.")
    return _user_out(full_user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return _user_out(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    _clear_session_cookie(response)


# ── Change password ───────────────────────────────────────────────────────────

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("current_password", "new_password", "confirm_password")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v:
            raise ValueError("must not be empty")
        return v


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePasswordRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if body.new_password != body.confirm_password:
        raise HTTPException(status_code=422, detail="New passwords do not match.")

    if not _verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

    settings = get_auth_settings(db)
    pw_error = validate_password(body.new_password, settings)
    if pw_error:
        raise HTTPException(status_code=422, detail=pw_error)

    current_user.password_hash = _hash_password(body.new_password)
    current_user.updated_at = _now()

    # Invalidate all existing sessions for this user (session-management rule)
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.revoked_at.is_(None),
    ).update({"revoked_at": _now()})

    _audit(db, action="user.password_change", actor_id=current_user.id, target_id=current_user.id)
    db.commit()

    # Force re-login by clearing the session cookie
    _clear_session_cookie(response)
