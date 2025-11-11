"""Setting up the application"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from context_async_sqlalchemy import (
    master_connect,
    replica_connect,
    fastapi_db_session_middleware,
)

from .database import create_engine, create_session_maker
from .routes.atomic_usage import handler_with_db_session_and_atomic
from .routes.manual_commit import handler_with_db_session_and_manual_close
from .routes.manual_rollback import handler_with_db_session_and_manual_rollback
from .routes.multiple_session_usage import handler_multiple_sessions

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
    setup_middlewares(app)
    setup_routes(app)
    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """Database connection lifecycle management"""
    await setup_database()
    yield
    await asyncio.gather(
        master_connect.close(),  # Close the engine if it was open
        replica_connect.close(),  # Close the engine if it was open
    )


def setup_middlewares(app: FastAPI) -> None:
    """
    The middleware will be responsible for initializing the context.
    And will also be responsible for autocommit or autorollback.
    """
    app.add_middleware(
        BaseHTTPMiddleware, dispatch=fastapi_db_session_middleware
    )


async def setup_database() -> None:
    """
    Here you pass the database connection parameters to the library.
    More specifically, the engine and session maker.
    """
    master_connect.engine_creator = create_engine
    master_connect.session_maker_creator = create_session_maker
    await master_connect.connect("127.0.0.1")


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
