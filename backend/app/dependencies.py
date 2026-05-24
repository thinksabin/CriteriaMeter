from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

import jwt

from app.config import JWT_ALGORITHM, SECRET_KEY
from app.db import get_db
from app.models.user import Group, GroupRole, User, UserGroup, UserRole


def _load_user_with_roles(db: Session, user_id: str) -> User | None:
    return (
        db.query(User)
        .options(
            joinedload(User.user_roles).joinedload(UserRole.role),
            joinedload(User.user_groups)
                .joinedload(UserGroup.group)
                .joinedload(Group.group_roles)
                .joinedload(GroupRole.role),
        )
        .filter(User.id == user_id, User.is_active == 1)
        .first()
    )


def effective_role_names(user: User) -> set[str]:
    roles: set[str] = {ur.role.name for ur in user.user_roles}
    for ug in user.user_groups:
        for gr in ug.group.group_roles:
            roles.add(gr.role.name)
    return roles


def get_current_user(
    cm_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not cm_token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    try:
        payload = jwt.decode(cm_token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid session.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid session.")

    user = _load_user_with_roles(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if "admin" not in effective_role_names(user):
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user
