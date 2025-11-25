# How middleware works

Most of the work - and the “magic” - happens inside the middleware.

Here is a diagram describing how it works.

![middleware_schema.png](img/middleware_schema.png)

At the beginning of a request, the middleware initializes a new
asynchronous context.
This asynchronous context is implemented using a contextvar.
It holds a mutable container that stores sessions.

A mutable container is used so that any coroutine, at any level, can
create, modify, or close sessions, and those changes will
affect the execution of the entire request.

Whenever your code accesses the library’s functionality, it interacts with
this container.

Finally, the middleware checks the container for any active sessions and
open transactions.
If transactions are open, they are either committed when the query
execution is successful or rolled back if it fails.
After that, all sessions are closed.

That’s precisely why you can safely close transactions and sessions early.
The middleware simply works with whatever is in the container:
if there’s anything left, it will close it properly; if you’ve
already handled it yourself, the middleware only needs to reset the context.

## Code example
The library aims to provide ready-made solutions so that you don’t have to
worry about these details - but they’re not always available.

So, let’s take a look at how Starlette middleware works.
You can use this example as a reference to implement your own.

[CODE](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/context_async_sqlalchemy/starlette_utils/http_middleware.py#L34)

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
