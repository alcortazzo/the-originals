import uuid
from datetime import datetime, timezone

from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


task_assignees = Table(
    "task_assignees",
    Base.metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.uuid"), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.uuid"), primary_key=True),
)


class Task(Base):
    __tablename__ = "tasks"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(length=255), nullable=False)
    description = Column(String(length=1024), nullable=True)
    coordinator_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    coordinator = relationship("User", back_populates="coordinated_tasks")
    assignees = relationship("User", secondary=task_assignees, back_populates="assigned_tasks")
    status = Column(String(length=50), nullable=False)
    priority = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=utcnow, nullable=False)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f"<Task(uuid={self.uuid}, name={self.name}, status={self.status}, priority={self.priority})>"


class User(Base):
    __tablename__ = "users"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=50), nullable=False)
    username = Column(String(length=50), unique=True, nullable=False, index=True)
    email = Column(String(length=255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(length=255), nullable=False)

    coordinated_tasks = relationship("Task", back_populates="coordinator")
    assigned_tasks = relationship("Task", secondary=task_assignees, back_populates="assignees")
    sessions = relationship("CookieSession", back_populates="user")

    role = Column(String(length=50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f"<User(uuid={self.uuid}, username={self.username}, email={self.email})>"


class CookieSession(Base):
    __tablename__ = "sessions"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    user = relationship("User", back_populates="sessions")

    token = Column(String(length=255), nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f"<Session(uuid={self.uuid}, user_uuid={self.user_uuid}, expires_at={self.expires_at})>"
