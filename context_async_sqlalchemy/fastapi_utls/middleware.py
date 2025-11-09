from fastapi import Request
from starlette.middleware.base import (  # type: ignore[attr-defined]
    Response,
    RequestResponseEndpoint,
)

from ..auto_commit import auto_commit_by_status_code
from ..context import (
    init_db_session_ctx,
    is_context_initiated,
    reset_db_session_ctx,
)
from ..session import rollback_db_session


async def fastapi_db_session_middleware(
    request: Request, call_next: RequestResponseEndpoint
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
    # session first, the dictionary itself is shared, and this coroutine will
    # add the session to dictionary = shared context.
    token = init_db_session_ctx()
    try:
        response = await call_next(request)
        await auto_commit_by_status_code(response.status_code)
        return response
    except Exception:
        await rollback_db_session()
        raise
    finally:
        await reset_db_session_ctx(token)
