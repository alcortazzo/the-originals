import multiprocessing
import uuid
from datetime import datetime, timedelta, timezone

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from api import utils
from api.validator import CookieSessionForm, TaskForm, UserForm
from database.database import Database
from database.models import Task, User

API_PORT = 8000
API_DEBUG = False


def create_app() -> FastAPI:
    app = FastAPI(
        title="Task Tracker",
        # Disabled debug, docs, and redoc pages for example of production-ready app
        debug=API_DEBUG,
        docs_url=None,
        redoc_url=None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Example of React frontend
        ],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    return app


app: FastAPI = create_app()

#
# ---- Example of Login/Logout and Task Creation Endpoints ----
#


@app.post("/v1/login")
async def login(user_form: UserForm, response: Response, request: Request) -> dict:
    """Login endpoint to authenticate the user

    Args:
        user_form (UserForm): Pydantic model for user login
        response (Response): FastAPI Response object
        request (Request): FastAPI Request object

    Raises:
        HTTPException: If the user is not authenticated

    Returns:
        dict: JSON response with error code and description
    """
    print(f"User {user_form.username} is trying to login")

    with Database() as db:
        user: User | None = db.check_if_user_exists(
            username=user_form.username, hashed_password=user_form.hashed_password
        )
        if user is None:
            raise HTTPException(status_code=403, detail="Incorrect username or password")

        now = datetime.now(tz=timezone.utc)
        auth_token = CookieSessionForm(
            user_uuid=user.uuid,
            token=str(uuid.uuid4()),
            expires_at=now + timedelta(hours=24),
            created_at=now,
        )
        db.create_session(**auth_token.model_dump())

        response.set_cookie(key="token", value=auth_token.token, httponly=False)
        response.set_cookie(key="role", value=user.role, httponly=False)
    return {"error": {"code": 0}, "result": {"description": "Success!"}}


@app.delete("/v1/logout", status_code=401)
async def logout(request: Request) -> Response:
    """Logout endpoint to deactivate the user session

    Args:
        request (Request): FastAPI Request object

    Raises:
        HTTPException: If the user is not authenticated

    Returns:
        Response: FastAPI Response object with status code 401
    """
    token = request.headers.get("authorization")
    if not token:
        raise HTTPException(status_code=401, detail="No authorization token provided")

    with Database() as db:
        db.deactivate_session(token)
    return Response(status_code=401)


@app.post(
    "/v1/create_task",
    dependencies=[
        # Check if user is authenticated and has the correct role
        Depends(utils.check_auth_token),
        Depends(utils.check_user_role(allowed_roles=["admin", "user"])),
    ],
)
async def create_task(body: TaskForm) -> dict:
    """Create a new task with the provided details validated by Pydantic model

    Args:
        body (TaskForm): Pydantic model for task creation

    Returns:
        dict: JSON response with error code, description, and task UUID
    """
    with Database() as db:
        # Get the coordinator and assignees from the database to ensure they exist
        coordinator: User = db.get_user_by_uuid(user_uuid=body.coordinator, raise_if_none=True)
        assignees: list[User] = [
            db.get_user_by_uuid(user_uuid=assignee, raise_if_none=True) for assignee in body.assignees
        ]

        pass

        # Create the task in the database
        task: Task = db.create_task(
            name=body.name,
            description=body.description,
            status=body.status,
            priority=body.priority,
            coordinator=coordinator,
            assignees=assignees,
        )
    return {"error": {"code": 0}, "result": {"description": "Success!", "task_uuid": task.uuid}}


@app.get(
    "/v1/get_tasks",
    dependencies=[
        # Check if user is authenticated and has the correct role
        Depends(utils.check_auth_token),
        Depends(utils.check_user_role(allowed_roles=["admin", "user"])),
    ],
)
async def get_tasks() -> dict:
    with Database() as db:
        tasks: list[Task] = db.get_tasks()
        tasks_to_return: list[dict] = []
        for task in tasks:
            tasks_to_return.append(
                {
                    "uuid": str(task.uuid),
                    "name": task.name,
                    "description": task.description,
                    "coordinator": str(task.coordinator.uuid),
                    "assignees": [str(a.uuid) for a in task.assignees],
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                    "last_updated": task.last_updated.isoformat(),
                }
            )

        return {"error": {"code": 0}, "result": {"description": "Success!", "tasks": tasks_to_return}}


if __name__ == "__main__":
    print(f"Starting API on port {API_PORT}")
    print(f"Number of CPUs: {multiprocessing.cpu_count() + 1 if not API_DEBUG else None}")
    uvicorn.run(
        "api.__main__:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=API_DEBUG,
        workers=multiprocessing.cpu_count() + 1 if not API_DEBUG else None,
    )
