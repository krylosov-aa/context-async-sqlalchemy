"""Setting up the application"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from starlette.applications import Starlette
from starlette.routing import Route

from context_async_sqlalchemy.starlette_utils import (
    add_starlette_http_db_session_middleware,
)

from examples.database import connection
from .routes.atomic import atomic_base_example
from .routes.atomic_prev_transaction import atomic_and_previous_transaction
from .routes.auto_rollback_by_exception import auto_rollback_by_exception
from .routes.auto_rollback_by_status_code import auto_rollback_by_status_code
from .routes.councurrent_queries import concurrent_queries
from .routes.early_commit import early_commit
from .routes.early_connection_close import early_connection_close
from .routes.early_rollback import early_rollback
from .routes.simple_usage import simple_usage


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
        "/atomic_base_example",
        atomic_base_example,
        methods=["POST"],
    ),
    Route(
        "/atomic_and_previous_transaction",
        atomic_and_previous_transaction,
        methods=["POST"],
    ),
    Route(
        "/simple_usage",
        simple_usage,
        methods=["POST"],
    ),
    Route(
        "/early_commit",
        early_commit,
        methods=["POST"],
    ),
    Route(
        "/concurrent_queries",
        concurrent_queries,
        methods=["POST"],
    ),
    Route(
        "/early_rollback",
        early_rollback,
        methods=["POST"],
    ),
    Route(
        "/auto_rollback_by_exception",
        auto_rollback_by_exception,
        methods=["POST"],
    ),
    Route(
        "/auto_rollback_by_status_code",
        auto_rollback_by_status_code,
        methods=["POST"],
    ),
    Route(
        "/early_connection_close",
        early_connection_close,
        methods=["POST"],
    ),
]
