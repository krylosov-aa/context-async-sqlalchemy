from fastapi import FastAPI
from starlette.middleware.base import (
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from ..auto_commit import (
    BeforeCommitCallback,
)
from ..starlette_utils import (
    add_starlette_http_db_session_middleware,
    starlette_http_db_session_middleware,
)


def add_fastapi_http_db_session_middleware(
    app: FastAPI,
    before_commit: BeforeCommitCallback | None = None,
) -> None:
    """Adds middleware to the application"""
    add_starlette_http_db_session_middleware(
        app,
        before_commit=before_commit,
    )


async def fastapi_http_db_session_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
    before_commit: BeforeCommitCallback | None = None,
) -> Response:
    """
    Database session lifecycle management.
    The session itself is created on demand in db_session().

    Transaction auto-commit is implemented if there is no exception and
        the response status is < 400. Otherwise, a rollback is performed.

    But you can commit or rollback manually in the handler.
    """
    return await starlette_http_db_session_middleware(
        request,
        call_next,
        before_commit=before_commit,
    )
