from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from fastapi import Header, HTTPException, Request

from database.database import Database
from database.models import CookieSession


async def check_auth_token(request: Request) -> None:
    """Check if the user is authenticated and the token is valid

    Args:
        request (Request): FastAPI Request object

    Raises:
        HTTPException: If the user is not authenticated or the token is invalid
    """
    token: str | None = request.headers.get("authorization")
    role: str | None = request.headers.get("role")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not role:
        raise HTTPException(status_code=401, detail="Unauthorized")

    with Database() as db:
        cookie_session: CookieSession | None = db.get_session(token=token)
        if not cookie_session:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if cookie_session.expires_at < datetime.now():
            db.deactivate_session(token=token)
            raise HTTPException(status_code=401, detail="Unauthorized")

        if cookie_session.user.role != role:
            raise HTTPException(status_code=401, detail="Unauthorized")

        expires_at = datetime.now(tz=timezone.utc) + timedelta(weeks=4)
        db.update_token_expires_at(token=token, expires_at=expires_at)


def check_user_role(allowed_roles: list[str]) -> Callable:
    """Check if the user has the correct role, allowed for specific operations

    Args:
        allowed_roles (list[str]): List of roles allowed for the operation

    Returns:
        Callable: Function to check if the user has the correct role
    """

    def _check_user_role(role: Optional[str] = Header(None)) -> None:
        if not role or role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not allowed")

    return _check_user_role
