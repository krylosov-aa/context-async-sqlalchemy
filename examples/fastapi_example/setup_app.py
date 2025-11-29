"""Setting up the application"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI

from context_async_sqlalchemy.fastapi_utils import (
    add_fastapi_http_db_session_middleware,
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


def setup_app() -> FastAPI:
    """
    A convenient entry point for app configuration.
    Convenient for testing.

    You don't have to follow my example here.
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
        "/atomic_base_example",
        atomic_base_example,
        methods=["POST"],
    )
    app.add_api_route(
        "/atomic_and_previous_transaction",
        atomic_and_previous_transaction,
        methods=["POST"],
    )
    app.add_api_route(
        "/simple_usage",
        simple_usage,
        methods=["POST"],
    )
    app.add_api_route(
        "/early_commit",
        early_commit,
        methods=["POST"],
    )
    app.add_api_route(
        "/concurrent_queries",
        concurrent_queries,
        methods=["POST"],
    )
    app.add_api_route(
        "/early_rollback",
        early_rollback,
        methods=["POST"],
    )
    app.add_api_route(
        "/auto_rollback_by_exception",
        auto_rollback_by_exception,
        methods=["POST"],
    )
    app.add_api_route(
        "/auto_rollback_by_status_code",
        auto_rollback_by_status_code,
        methods=["POST"],
    )
    app.add_api_route(
        "/early_connection_close",
        early_connection_close,
        methods=["POST"],
    )
