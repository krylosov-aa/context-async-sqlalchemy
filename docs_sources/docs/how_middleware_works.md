# How middleware works

The biggest part of the work and magic happens in middleware.
The library strives to provide ready-made solutions so that you don't have to
worry. But they are not always there.
Therefore, we will tell you how starlette middleware works,
using the example of which you can write your own.


```python
from starlette.middleware.base import (  # type: ignore[attr-defined]
    Request,
    Response,
    RequestResponseEndpoint,
    BaseHTTPMiddleware,
)

from context_async_sqlalchemy import (
    init_db_session_ctx,
    is_context_initiated,
    reset_db_session_ctx,
    auto_commit_by_status_code,
    rollback_all_sessions,
)

async def starlette_http_db_session_middleware(
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
    # session first, the container itself is shared, and this coroutine will
    # add the session to container = shared context.
    token = init_db_session_ctx()
    try:
        response = await call_next(request)
        # using the status code, we decide to commit or rollback all sessions
        await auto_commit_by_status_code(response.status_code)
        return response
    except Exception:
        # If an exception occurs, we roll all sessions back
        await rollback_all_sessions()
        raise
    finally:
        # Close all sessions and clear the context
        await reset_db_session_ctx(token)
```
