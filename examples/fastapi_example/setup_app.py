"""Setting up the application"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI

from context_async_sqlalchemy.fastapi_utils import (
    add_fastapi_http_db_session_middleware,
)

from .database import connection
from .routes.atomic_usage import handler_with_db_session_and_atomic
from .routes.manual_commit import handler_with_db_session_and_manual_close
from .routes.manual_rollback import handler_with_db_session_and_manual_rollback
from .routes.multiple_session_usage import handler_multiple_sessions
from .routes.early_connection_close import handler_with_early_connection_close

from .routes.simple_usage import handler_with_db_session
from .routes.simple_with_exception import handler_with_db_session_and_exception
from .routes.simple_with_http_exception import (
    handler_with_db_session_and_http_exception,
)


def setup_app() -> FastAPI:
    """
    A convenient entry point for app configuration.
    Convenient for testing.
    You don't have to follow my example (though I recommend it).
    """
    app = FastAPI(
        lifespan=lifespan,
    )
    add_fastapi_http_db_session_middleware(app)
    setup_routes(app)
    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """Database connection lifecycle management"""
    yield
    await connection.close()  # Close the engine if it was open


def setup_routes(app: FastAPI) -> None:
    """
    It's just a single point where I collected all the APIs.
    You don't have to do it exactly like this. I just prefer it that way.
    """
    app.add_api_route(
        "/example_with_db_session",
        handler_with_db_session,
        methods=["POST"],
    )
    app.add_api_route(
        "/example_with_db_session_and_atomic",
        handler_with_db_session_and_atomic,
        methods=["POST"],
    )
    app.add_api_route(
        "/example_with_db_session_and_manual_close",
        handler_with_db_session_and_manual_close,
        methods=["POST"],
    )
    app.add_api_route(
        "/example_multiple_sessions",
        handler_multiple_sessions,
        methods=["POST"],
    )
    app.add_api_route(
        "/example_with_manual_rollback",
        handler_with_db_session_and_manual_rollback,
        methods=["POST"],
    )
    app.add_api_route(
        "/example_with_exception",
        handler_with_db_session_and_exception,
        methods=["POST"],
    )
    app.add_api_route(
        "/example_with_http_exception",
        handler_with_db_session_and_http_exception,
        methods=["POST"],
    )
    app.add_api_route(
        "/example_with_early_connection_close",
        handler_with_early_connection_close,
        methods=["POST"],
    )
