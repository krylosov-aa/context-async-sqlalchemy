"""Setting up the application"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from starlette.applications import Starlette
from starlette.routing import Route

from context_async_sqlalchemy.starlette_utils import (
    add_starlette_http_db_session_middleware,
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


def setup_app() -> Starlette:
    """
    A convenient entry point for app configuration.
    Convenient for testing.

    You don't have to follow my example here.
    """
    app = Starlette(
        debug=True,
        routes=_routes,
        lifespan=lifespan,
    )

    add_starlette_http_db_session_middleware(app)
    return app


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[None, Any]:
    """Database connection lifecycle management"""
    yield
    await connection.close()  # Close the engine if it was open


_routes = [
    Route(
        "/example_with_db_session",
        handler_with_db_session,
        methods=["POST"],
    ),
    Route(
        "/example_with_db_session_and_atomic",
        handler_with_db_session_and_atomic,
        methods=["POST"],
    ),
    Route(
        "/example_with_db_session_and_manual_close",
        handler_with_db_session_and_manual_close,
        methods=["POST"],
    ),
    Route(
        "/example_multiple_sessions",
        handler_multiple_sessions,
        methods=["POST"],
    ),
    Route(
        "/example_with_manual_rollback",
        handler_with_db_session_and_manual_rollback,
        methods=["POST"],
    ),
    Route(
        "/example_with_exception",
        handler_with_db_session_and_exception,
        methods=["POST"],
    ),
    Route(
        "/example_with_http_exception",
        handler_with_db_session_and_http_exception,
        methods=["POST"],
    ),
    Route(
        "/example_with_early_connection_close",
        handler_with_early_connection_close,
        methods=["POST"],
    ),
]
