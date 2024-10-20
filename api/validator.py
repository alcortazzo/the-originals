from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, field_validator


class CookieSessionForm(BaseModel):
    user_uuid: str
    token: str
    created_at: datetime
    expires_at: datetime

    @field_validator("created_at", "expires_at", mode="before")
    def created_at_validator(cls, v):
        if not isinstance(v, datetime):
            raise ValueError("created_at and expires_at must be datetime objects")
        return v.astimezone(tz=timezone.utc)


class UserForm(BaseModel):
    username: str
    hashed_password: str

    class Config:
        anystr_strip_whitespace = True

    @field_validator("username")
    def username_validator(cls, v):
        if not v:
            raise ValueError("Username cannot be empty")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not v.isalnum():
            raise ValueError("Username can only contain alphanumeric characters")
        return v

    @field_validator("hashed_password")
    def password_validator(cls, v):
        if not v:
            raise ValueError("Password cannot be empty")
        return v


class TaskForm(BaseModel):
    name: str
    description: str | None
    coordinator: UUID
    assignees: list[UUID]

    status: Literal["TODO", "In Progress", "Done"]
    priority: int

    class Config:
        anystr_strip_whitespace = True

    @field_validator("name")
    def name_validator(cls, v):
        if not v:
            raise ValueError("Name cannot be empty")
        if len(v) < 3:
            raise ValueError("Name must be at least 3 characters long")
        return v

    @field_validator("assignees")
    def assignees_validator(cls, v):
        if not v:
            raise ValueError("Assignees cannot be empty")
        return v
