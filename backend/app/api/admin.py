import datetime
import uuid

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth_utils import AuthSettings, get_auth_settings
from app.db import get_db
from app.models.settings import AppSetting
from app.models.user import Group, GroupRole, Role, User, UserGroup, UserRole

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _now() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _fetch_user(db: Session, uid: str) -> User:
    user = (
        db.query(User)
        .options(
            joinedload(User.user_roles).joinedload(UserRole.role),
            joinedload(User.user_groups).joinedload(UserGroup.group),
        )
        .filter(User.id == uid)
        .first()
    )
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    return user


def _fetch_group(db: Session, gid: int) -> Group:
    group = (
        db.query(Group)
        .options(joinedload(Group.group_roles).joinedload(GroupRole.role))
        .filter(Group.id == gid)
        .first()
    )
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    return group


# ── Schemas ────────────────────────────────────────────────────────────────────

class AdminUserOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    mobile_number: str | None
    is_active: bool
    api_access: bool
    email_verified: bool
    last_login_at: str | None
    created_at: str
    roles: list[str]
    groups: list[str]


class UserCreateBody(BaseModel):
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
    def min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("must be at least 8 characters")
        return v


class UserUpdateBody(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    mobile_number: str | None = None


class AdminRoleOut(BaseModel):
    id: int
    name: str
    description: str | None
    user_count: int


class RoleCreateBody(BaseModel):
    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v


class RoleUpdateBody(BaseModel):
    name: str | None = None
    description: str | None = None


class AdminGroupOut(BaseModel):
    id: int
    name: str
    description: str | None
    roles: list[str]
    member_count: int
    created_at: str


class GroupCreateBody(BaseModel):
    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("must not be empty")
        if not v.isalnum():
            raise ValueError("must contain only alphanumeric characters (a–z, 0–9)")
        return v


class GroupUpdateBody(BaseModel):
    name: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lower()
        if not v:
            raise ValueError("must not be empty")
        if not v.isalnum():
            raise ValueError("must contain only alphanumeric characters (a–z, 0–9)")
        return v


# ── Helpers ────────────────────────────────────────────────────────────────────

def _user_out(user: User) -> AdminUserOut:
    return AdminUserOut(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        mobile_number=user.mobile_number,
        is_active=bool(user.is_active),
        api_access=bool(user.api_access),
        email_verified=bool(user.email_verified),
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        roles=[ur.role.name for ur in user.user_roles],
        groups=[ug.group.name for ug in user.user_groups],
    )


def _role_out(role: Role, db: Session) -> AdminRoleOut:
    count = db.query(UserRole).filter(UserRole.role_id == role.id).count()
    return AdminRoleOut(
        id=role.id,
        name=role.name,
        description=role.description,
        user_count=count,
    )


def _group_out(group: Group, db: Session) -> AdminGroupOut:
    count = db.query(UserGroup).filter(UserGroup.group_id == group.id).count()
    return AdminGroupOut(
        id=group.id,
        name=group.name,
        description=group.description,
        roles=[gr.role.name for gr in group.group_roles],
        member_count=count,
        created_at=group.created_at,
    )


# ── Users ──────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[AdminUserOut])
def list_users(db: Session = Depends(get_db)) -> list[AdminUserOut]:
    users = (
        db.query(User)
        .options(
            joinedload(User.user_roles).joinedload(UserRole.role),
            joinedload(User.user_groups).joinedload(UserGroup.group),
        )
        .all()
    )
    return [_user_out(u) for u in users]


@router.post("/users", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreateBody, db: Session = Depends(get_db)) -> AdminUserOut:
    if db.query(User).filter(func.lower(User.email) == body.email.strip().lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered.")
    user = User(
        id=str(uuid.uuid4()),
        first_name=body.first_name.strip(),
        last_name=body.last_name.strip(),
        email=body.email.strip(),
        mobile_number=body.mobile_number or None,
        password_hash=_hash_password(body.password),
        email_verified=0,
        is_active=1,
        api_access=1,
        created_at=_now(),
        updated_at=_now(),
    )
    db.add(user)
    db.commit()
    return _user_out(_fetch_user(db, user.id))


@router.patch("/users/{uid}", response_model=AdminUserOut)
def update_user(uid: str, body: UserUpdateBody, db: Session = Depends(get_db)) -> AdminUserOut:
    user = db.get(User, uid)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if body.first_name is not None:
        user.first_name = body.first_name.strip()
    if body.last_name is not None:
        user.last_name = body.last_name.strip()
    if body.email is not None:
        email = body.email.strip()
        dup = db.query(User).filter(
            func.lower(User.email) == email.lower(), User.id != uid
        ).first()
        if dup:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already in use.")
        user.email = email
    if body.mobile_number is not None:
        user.mobile_number = body.mobile_number or None
    db.commit()
    return _user_out(_fetch_user(db, uid))


@router.delete("/users/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(uid: str, db: Session = Depends(get_db)) -> None:
    user = db.get(User, uid)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    db.delete(user)
    db.commit()


@router.patch("/users/{uid}/toggle-active", response_model=AdminUserOut)
def toggle_active(uid: str, db: Session = Depends(get_db)) -> AdminUserOut:
    user = db.get(User, uid)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    user.is_active = 0 if user.is_active else 1
    db.commit()
    return _user_out(_fetch_user(db, uid))


@router.patch("/users/{uid}/toggle-api", response_model=AdminUserOut)
def toggle_api_access(uid: str, db: Session = Depends(get_db)) -> AdminUserOut:
    user = db.get(User, uid)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    user.api_access = 0 if user.api_access else 1
    db.commit()
    return _user_out(_fetch_user(db, uid))


# ── Direct role assignment (user ↔ role) ───────────────────────────────────────

@router.put("/users/{uid}/roles/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def assign_role(uid: str, rid: int, db: Session = Depends(get_db)) -> None:
    if not db.get(User, uid):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if not db.get(Role, rid):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")
    exists = db.query(UserRole).filter(
        UserRole.user_id == uid, UserRole.role_id == rid
    ).first()
    if not exists:
        db.add(UserRole(user_id=uid, role_id=rid, granted_at=_now()))
        db.commit()


@router.delete("/users/{uid}/roles/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_role(uid: str, rid: int, db: Session = Depends(get_db)) -> None:
    ur = db.query(UserRole).filter(
        UserRole.user_id == uid, UserRole.role_id == rid
    ).first()
    if ur:
        db.delete(ur)
        db.commit()


# ── Group membership (user ↔ group) ───────────────────────────────────────────

@router.put("/users/{uid}/groups/{gid}", status_code=status.HTTP_204_NO_CONTENT)
def add_user_to_group(uid: str, gid: int, db: Session = Depends(get_db)) -> None:
    if not db.get(User, uid):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if not db.get(Group, gid):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    exists = db.query(UserGroup).filter(
        UserGroup.user_id == uid, UserGroup.group_id == gid
    ).first()
    if not exists:
        db.add(UserGroup(user_id=uid, group_id=gid, joined_at=_now()))
        db.commit()


@router.delete("/users/{uid}/groups/{gid}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_group(uid: str, gid: int, db: Session = Depends(get_db)) -> None:
    ug = db.query(UserGroup).filter(
        UserGroup.user_id == uid, UserGroup.group_id == gid
    ).first()
    if ug:
        db.delete(ug)
        db.commit()


# ── Roles ──────────────────────────────────────────────────────────────────────

@router.get("/roles", response_model=list[AdminRoleOut])
def list_roles(db: Session = Depends(get_db)) -> list[AdminRoleOut]:
    roles = db.query(Role).order_by(Role.name).all()
    return [_role_out(r, db) for r in roles]


@router.post("/roles", response_model=AdminRoleOut, status_code=status.HTTP_201_CREATED)
def create_role(body: RoleCreateBody, db: Session = Depends(get_db)) -> AdminRoleOut:
    if db.query(Role).filter(Role.name == body.name.strip()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Role name already exists.")
    role = Role(name=body.name.strip(), description=body.description or None)
    db.add(role)
    db.commit()
    db.refresh(role)
    return _role_out(role, db)


@router.patch("/roles/{rid}", response_model=AdminRoleOut)
def update_role(rid: int, body: RoleUpdateBody, db: Session = Depends(get_db)) -> AdminRoleOut:
    role = db.get(Role, rid)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")
    if body.name is not None:
        name = body.name.strip()
        dup = db.query(Role).filter(Role.name == name, Role.id != rid).first()
        if dup:
            raise HTTPException(status.HTTP_409_CONFLICT, "Role name already in use.")
        role.name = name
    if body.description is not None:
        role.description = body.description or None
    db.commit()
    db.refresh(role)
    return _role_out(role, db)


@router.delete("/roles/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(rid: int, db: Session = Depends(get_db)) -> None:
    role = db.get(Role, rid)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")
    db.delete(role)
    db.commit()


# ── Groups ─────────────────────────────────────────────────────────────────────

@router.get("/groups", response_model=list[AdminGroupOut])
def list_groups(db: Session = Depends(get_db)) -> list[AdminGroupOut]:
    groups = (
        db.query(Group)
        .options(joinedload(Group.group_roles).joinedload(GroupRole.role))
        .order_by(Group.name)
        .all()
    )
    return [_group_out(g, db) for g in groups]


@router.post("/groups", response_model=AdminGroupOut, status_code=status.HTTP_201_CREATED)
def create_group(body: GroupCreateBody, db: Session = Depends(get_db)) -> AdminGroupOut:
    if db.query(Group).filter(Group.name == body.name.strip()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Group already exist.")
    group = Group(name=body.name.strip(), description=body.description or None,
                  created_at=_now(), updated_at=_now())
    db.add(group)
    db.commit()
    return _group_out(_fetch_group(db, group.id), db)


@router.patch("/groups/{gid}", response_model=AdminGroupOut)
def update_group(gid: int, body: GroupUpdateBody, db: Session = Depends(get_db)) -> AdminGroupOut:
    group = db.get(Group, gid)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    if body.name is not None:
        name = body.name  # already lowercased + validated by Pydantic
        dup = db.query(Group).filter(Group.name == name, Group.id != gid).first()
        if dup:
            raise HTTPException(status.HTTP_409_CONFLICT, "Group already exist.")
        group.name = name
    if body.description is not None:
        group.description = body.description or None
    db.commit()
    return _group_out(_fetch_group(db, gid), db)


@router.delete("/groups/{gid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(gid: int, db: Session = Depends(get_db)) -> None:
    group = db.get(Group, gid)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    db.delete(group)
    db.commit()


# ── Group role assignment (group ↔ role) ───────────────────────────────────────

@router.put("/groups/{gid}/roles/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def assign_group_role(gid: int, rid: int, db: Session = Depends(get_db)) -> None:
    if not db.get(Group, gid):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    if not db.get(Role, rid):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found.")
    exists = db.query(GroupRole).filter(
        GroupRole.group_id == gid, GroupRole.role_id == rid
    ).first()
    if not exists:
        db.add(GroupRole(group_id=gid, role_id=rid, granted_at=_now()))
        db.commit()


@router.delete("/groups/{gid}/roles/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_group_role(gid: int, rid: int, db: Session = Depends(get_db)) -> None:
    gr = db.query(GroupRole).filter(
        GroupRole.group_id == gid, GroupRole.role_id == rid
    ).first()
    if gr:
        db.delete(gr)
        db.commit()


# ── Group member management (group ↔ user) ─────────────────────────────────────

@router.put("/groups/{gid}/members/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def add_group_member(gid: int, uid: str, db: Session = Depends(get_db)) -> None:
    if not db.get(Group, gid):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    if not db.get(User, uid):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    exists = db.query(UserGroup).filter(
        UserGroup.group_id == gid, UserGroup.user_id == uid
    ).first()
    if not exists:
        db.add(UserGroup(user_id=uid, group_id=gid, joined_at=_now()))
        db.commit()


@router.delete("/groups/{gid}/members/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def remove_group_member(gid: int, uid: str, db: Session = Depends(get_db)) -> None:
    ug = db.query(UserGroup).filter(
        UserGroup.group_id == gid, UserGroup.user_id == uid
    ).first()
    if ug:
        db.delete(ug)
        db.commit()


# ── Authentication settings ────────────────────────────────────────────────────

class AuthSettingsOut(BaseModel):
    signup_enabled:       bool
    min_password_length:  int
    require_number:       bool
    require_uppercase:    bool
    require_special_char: bool


class AuthSettingsPatch(BaseModel):
    signup_enabled:       bool | None = None
    min_password_length:  int  | None = None
    require_number:       bool | None = None
    require_uppercase:    bool | None = None
    require_special_char: bool | None = None


def _settings_to_out(s: AuthSettings) -> AuthSettingsOut:
    return AuthSettingsOut(
        signup_enabled      = s.signup_enabled,
        min_password_length = s.min_password_length,
        require_number      = s.require_number,
        require_uppercase   = s.require_uppercase,
        require_special_char= s.require_special_char,
    )


@router.get("/auth-settings", response_model=AuthSettingsOut)
def get_auth_settings_endpoint(db: Session = Depends(get_db)) -> AuthSettingsOut:
    return _settings_to_out(get_auth_settings(db))


@router.patch("/auth-settings", response_model=AuthSettingsOut)
def update_auth_settings(body: AuthSettingsPatch, db: Session = Depends(get_db)) -> AuthSettingsOut:
    if body.min_password_length is not None and not (6 <= body.min_password_length <= 128):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Minimum password length must be between 6 and 128.")

    updates: dict[str, str] = {}
    if body.signup_enabled       is not None: updates["auth.signup_enabled"]       = str(body.signup_enabled).lower()
    if body.min_password_length  is not None: updates["auth.min_password_length"]  = str(body.min_password_length)
    if body.require_number       is not None: updates["auth.require_number"]        = str(body.require_number).lower()
    if body.require_uppercase    is not None: updates["auth.require_uppercase"]     = str(body.require_uppercase).lower()
    if body.require_special_char is not None: updates["auth.require_special_char"]  = str(body.require_special_char).lower()

    for key, val in updates.items():
        row = db.get(AppSetting, key)
        if row:
            row.value = val
        else:
            db.add(AppSetting(key=key, value=val))
    db.commit()

    return _settings_to_out(get_auth_settings(db))
