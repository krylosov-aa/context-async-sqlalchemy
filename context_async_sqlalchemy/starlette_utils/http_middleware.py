from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from starlette.applications import Starlette
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    DispatchFunction,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from ..auto_commit import (
    BeforeCommitCallback,
    auto_commit_by_status_code,
    rollback_all_sessions,
)
from ..context import (
    init_db_session_ctx,
    is_context_initiated,
    reset_db_session_ctx,
)

Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Scope = MutableMapping[str, Any]
Send = Callable[[Message], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


def add_starlette_http_db_session_middleware(
    app: Starlette,
    before_commit: BeforeCommitCallback | None = None,
) -> None:
    """Adds middleware to the application"""
    app.add_middleware(
        StarletteHTTPDBSessionMiddleware, before_commit=before_commit
    )


class StarletteHTTPDBSessionMiddleware(BaseHTTPMiddleware):
    """Database session lifecycle management."""

    def __init__(
        self,
        app: ASGIApp,
        dispatch: DispatchFunction | None = None,
        before_commit: BeforeCommitCallback | None = None,
    ):
        super().__init__(app, dispatch=dispatch)
        self._before_commit = before_commit

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        return await starlette_http_db_session_middleware(
            request,
            call_next,
            before_commit=self._before_commit,
        )


async def starlette_http_db_session_middleware(
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
    # Tests have different session management rules
    # so if the context variable is already set, we do nothing
    if is_context_initiated():
        return await call_next(request)

    # We set the context here, meaning all child coroutines will receive the
    # same context. And even if a child coroutine requests the
    # session first, the container itself is shared, and this coroutine will
    # add the session to container = shared context.
    token = init_db_session_ctx()
    try:
        response = await call_next(request)
        # using the status code, we decide to commit or rollback all sessions
        await auto_commit_by_status_code(
            status_code=response.status_code,
            before_commit=before_commit,
        )
        return response
    except Exception:
        # If an exception occurs, we roll all sessions back
        await rollback_all_sessions()
        raise
    finally:
        # Close all sessions and clear the context
        await reset_db_session_ctx(token)
