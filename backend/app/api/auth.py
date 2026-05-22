import datetime
import json
import uuid

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth_utils import get_auth_settings, validate_password
from app.config import JWT_ALGORITHM, JWT_EXPIRE_HOURS, SECRET_KEY
from app.db import get_db
from app.models.user import AuditLog, User

router = APIRouter(prefix="/api/auth", tags=["auth"])


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


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _make_token(user_id: str) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=JWT_ALGORITHM)


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
    return UserOut(id=user.id, email=user.email,
                   first_name=user.first_name, last_name=user.last_name)


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
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

    return LoginResponse(
        access_token=_make_token(user.id),
        user=UserOut(id=user.id, email=user.email,
                     first_name=user.first_name, last_name=user.last_name),
    )
