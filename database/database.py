from contextlib import suppress
from datetime import datetime
from typing import Literal
from uuid import UUID

import sqlalchemy as sa
from loguru import logger
from sqlalchemy import Engine, engine, update
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_random

from database.models import Base, CookieSession, Task, User


class Database:
    def __init__(self):
        connection_url: engine.url.URL = engine.url.URL.create(
            drivername="sqlite",
            database="./database.db",
        )
        self.engine: Engine = sa.create_engine(
            url=connection_url,
            echo=False,
        )
        # Base.metadata.create_all(self.engine)
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = Session(bind=self.engine)
            logger.debug("Database session created")
        return self._session

    def close(self):
        with suppress(Exception):
            if self._session is not None:
                self._session.close()
                self._session = None
            self.engine.dispose()
            logger.debug("Database session closed")

    def __enter__(self, *args, **kwargs) -> "Database":
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    #
    # ---- Cookie Session Methods ----
    #

    def check_if_user_exists(self, username: str, hashed_password: str) -> User | None:
        query = (
            self.session.query(User)
            .filter(
                User.username == username,
                User.hashed_password == hashed_password,
                User.is_active.is_(True),
            )
            .first()
        )
        return query

    @retry(stop=stop_after_attempt(2), wait=wait_random(min=1, max=3), reraise=True)
    def create_session(self, user_uuid: str, token: str, created_at: datetime, expires_at: datetime) -> None:
        try:
            cookie_session = CookieSession(
                user_uuid=user_uuid,
                token=token,
                created_at=created_at,
                expires_at=expires_at,
            )
            self.session.add(instance=cookie_session)
            self.session.commit()
        except Exception as ex:
            self.session.rollback()
            raise ex

    @retry(stop=stop_after_attempt(2), wait=wait_random(min=1, max=3), reraise=True)
    def deactivate_session(self, token: str) -> None:
        query = update(CookieSession).where(CookieSession.token == token).values(is_active=False)
        try:
            self.session.execute(query)
            self.session.commit()
        except Exception as ex:
            self.session.rollback()
            raise ex

    def get_session(self, token: str) -> CookieSession | None:
        query = self.session.query(CookieSession).filter(CookieSession.token == token).first()
        return query

    @retry(stop=stop_after_attempt(2), wait=wait_random(min=1, max=3), reraise=True)
    def update_token_expires_at(self, token: str, expires_at: datetime) -> None:
        query = update(CookieSession).where(CookieSession.token == token).values(expires_at=expires_at)
        try:
            self.session.execute(query)
            self.session.commit()
        except Exception as ex:
            self.session.rollback()
            raise ex

    #
    # ---- Task Methods ----
    #

    def get_user_by_uuid(self, user_uuid: UUID, raise_if_none: bool = False) -> User | None:
        query = self.session.query(User).filter(User.uuid == user_uuid).first()
        if not query and raise_if_none:
            raise Exception(f"User with uuid {user_uuid} not found in the database")
        return query

    @retry(stop=stop_after_attempt(2), wait=wait_random(min=1, max=3), reraise=True)
    def create_task(
        self,
        name: str,
        description: str | None,
        status: Literal["TODO", "In Progress", "Done"],
        priority: int,
        coordinator: User,
        assignees: list[User],
    ) -> Task:
        new_task = Task(
            name=name,
            description=description,
            status=status,
            priority=priority,
            coordinator_id=coordinator.uuid,
            coordinator=coordinator,
            assignees=assignees,
        )

        try:
            self.session.add(new_task)
            self.session.commit()
        except Exception as ex:
            self.session.rollback()
            raise ex
        return new_task

    def get_tasks(self) -> list[Task]:
        query = list(self.session.query(Task).all())
        return query
