import datetime
import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    mobile_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email_verified: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    api_access: Mapped[int] = mapped_column(Integer, default=1)
    last_login_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[str] = mapped_column(String(30), default=_now)
    updated_at: Mapped[str] = mapped_column(String(30), default=_now)

    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        foreign_keys="[UserRole.user_id]",
        cascade="all, delete-orphan",
    )
    user_groups: Mapped[list["UserGroup"]] = relationship(
        back_populates="user",
        foreign_keys="[UserGroup.user_id]",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    auth_tokens: Mapped[list["AuthToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_roles: Mapped[list["UserRole"]] = relationship(back_populates="role")
    group_roles: Mapped[list["GroupRole"]] = relationship(back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True
    )
    granted_at: Mapped[str] = mapped_column(String(30), default=_now)
    granted_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="user_roles", foreign_keys=[user_id])
    role: Mapped["Role"] = relationship(back_populates="user_roles")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(30), default=_now)
    updated_at: Mapped[str] = mapped_column(String(30), default=_now)

    group_roles: Mapped[list["GroupRole"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )
    user_groups: Mapped[list["UserGroup"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class GroupRole(Base):
    __tablename__ = "group_roles"

    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True
    )
    granted_at: Mapped[str] = mapped_column(String(30), default=_now)
    granted_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    group: Mapped["Group"] = relationship(back_populates="group_roles")
    role: Mapped["Role"] = relationship(back_populates="group_roles")


class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )
    joined_at: Mapped[str] = mapped_column(String(30), default=_now)
    added_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="user_groups", foreign_keys=[user_id])
    group: Mapped["Group"] = relationship(back_populates="user_groups")


class UserSession(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(255))
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[str] = mapped_column(String(30), default=_now)
    expires_at: Mapped[str] = mapped_column(String(30))
    revoked_at: Mapped[str | None] = mapped_column(String(30), nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    purpose: Mapped[str] = mapped_column(String(20))
    token_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[str] = mapped_column(String(30), default=_now)
    expires_at: Mapped[str] = mapped_column(String(30))
    consumed_at: Mapped[str | None] = mapped_column(String(30), nullable=True)

    user: Mapped["User"] = relationship(back_populates="auth_tokens")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100))
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    # 'metadata' is reserved by SQLAlchemy Base — map the column under a different attribute name
    meta: Mapped[str | None] = mapped_column("metadata", Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(30), default=_now)
