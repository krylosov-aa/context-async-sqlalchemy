# API Reference


## DBConnect

DBConnect is responsible for managing the engine and the session_maker.
You need to define two factories.
Optionally, you can specify a host to connect to.
You can also specify a handler that runs before a session is created -
this handler can be used to connect to the host for the first time or
to reconnect to a new one.

### init
```python
def __init__(
    self: DBConnect,
    engine_creator: EngineCreatorFunc,
    session_maker_creator: SessionMakerCreatorFunc,
    host: str | None = None,
    before_create_session_handler: AsyncFunc | None = None,
) -> None:
```

`engine_creator` is a factory function for creating engines.
It’s an asynchronous callable that takes a host as input and returns
an async engine.

[Example](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/examples/fastapi_example/database.py#L15)


`session_maker_creator` is a factory function for creating an asynchronous
session_maker.
It’s an asynchronous callable that takes an async engine as input and returns
an async session_maker.

[Example](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/examples/fastapi_example/database.py#L35)

`host` is an optional parameter.
You can specify only this parameter to make your connection always work with
a single host, without dynamic switching.
However, you can still change the host in the handler if needed - it won’t
cause any issues.

`before_create_session_handler` is a handler that allows you to execute
custom logic before creating a session.
For example, you can switch the host to another one - this is useful for
dynamically determining the master if the previous master fails and a
replica takes its place.

The handler is an asynchronous callable that takes a DBConnect instance
as input and returns nothing.

Example:
```python
async def renew_master_connect(connect: DBConnect) -> None:
    """Updates the host if the master has changed"""
    master_host = await get_master()
    if master_host != connect.host:
        await connect.change_host(master_host)
```

---

### connect

```python
async def connect(self: DBConnect, host: str) -> None:
```
Establishes a connection to the specified host.
This method doesn’t need to be called explicitly.
If it isn’t called, the first session request will automatically
establish the connection.

---

### change_host

```python
async def change_host(self: DBConnect, host: str) -> None:
```
Establishes a connection to the specified host, but first
checks under a lock that the currently connected host is different
from the target host.

---

### create_session

```python
async def create_session(self: DBConnect) -> AsyncSession:
```
Creates a new session. Used internally by the library -
you’ll probably never need to call it directly, but it’s
good to know it exists.

---

### session_maker

```python
async def session_maker(self: DBConnect) -> async_sessionmaker[AsyncSession]:
```
Provides access to the session_maker currently used to create sessions.


---

### close

```python
async def close(self: DBConnect) -> None:
```
Completely closes and cleans up all resources, freeing the connection pool.
This should be called at the end of your application’s lifecycle.



## Middlewares

Most of the work - and the “magic” - happens inside the middleware.

You can check out [how it works](how_middleware_works.md) and implement your
own.

### Fastapi
```python
from context_async_sqlalchemy.fastapi_utils import (
    fastapi_http_db_session_middleware,
    add_fastapi_http_db_session_middleware,
)
app = FastAPI(...)


add_fastapi_http_db_session_middleware(app)

# OR

app.add_middleware(
    BaseHTTPMiddleware, dispatch=fastapi_http_db_session_middleware
)
```


### Starlette
```python
from context_async_sqlalchemy.starlette_utils import (
    add_starlette_http_db_session_middleware,
    starlette_http_db_session_middleware,
    StarletteHTTPDBSessionMiddleware,
)
app = Starlette(...)


add_starlette_http_db_session_middleware(app)

# OR

app.add_middleware(
    BaseHTTPMiddleware, dispatch=starlette_http_db_session_middleware
)
# OR

app.add_middleware(StarletteHTTPDBSessionMiddleware)
```


### Pure ASGI
```python
from context_async_sqlalchemy import (
    ASGIHTTPDBSessionMiddleware,
)
app = SomeASGIApp(...)

app.add_middleware(ASGIHTTPDBSessionMiddleware)
```


## Sessions

Here are the functions you’ll use most often from the library.
They allow you to work with sessions directly from your asynchronous code.

### db_session
```python
async def db_session(connect: DBConnect) -> AsyncSession:
```
The most important function for obtaining a session in your code.
When called for the first time, it returns a new session; subsequent
calls return the same session.

---

### atomic_db_session
```python
@asynccontextmanager
async def atomic_db_session(
    connect: DBConnect,
    current_transaction: Literal["commit", "rollback", "append", "raise"] = "commit",
) -> AsyncGenerator[AsyncSession, None]:
```
A context manager that can be used to wrap another function which
uses a context session, making that call isolated within its own transaction.

There are several options that define how the function will handle
an already open transaction.

current_transaction:

- `commit` - commits the open transaction and starts a new one
- `rollback` - rolls back the open transaction and starts a new one
- `append` - continues using the current transaction and commits it
- `raise` - raises an InvalidRequestError

---

### commit_db_session
```python
async def commit_db_session(connect: DBConnect) -> None:
```
Commits the active session, if there is one.

---

### rollback_db_session
```python
async def rollback_db_session(connect: DBConnect) -> None:
```
Rollbacks the active session, if there is one.

---

### close_db_session
```python
async def close_db_session(connect: DBConnect) -> None:
```
Closes the current context session. The connection is returned to the pool.
If you close an uncommitted transaction, the connection will be rolled back.

This is useful if, for example, at the beginning of the handle a
        database query is needed, and then there is some other long-term work
        and you don't want to keep the connection opened.

---

### new_non_ctx_session
```python
@asynccontextmanager
async def new_non_ctx_session(
    connect: DBConnect,
) -> AsyncGenerator[AsyncSession, None]:
```
A context manager that allows you to create a new session without placing
it in a context. It's used for manual session management when you
don't want to use a context.

---

### new_non_ctx_atomic_session
```python
@asynccontextmanager
async def new_non_ctx_atomic_session(
    connect: DBConnect,
) -> AsyncGenerator[AsyncSession, None]:
```
A context manager that allows you to create a new session with
a new transaction that isn't placed in a context. It's used for manual
session management when you don't want to use a context.


## Context

### run_in_new_ctx
```python
async def run_in_new_ctx(
    callable_func: AsyncCallable[AsyncCallableResult],
    *args: Any,
    **kwargs: Any,
) -> AsyncCallableResult:
```
Runs a function in a new context with new sessions that have their
        own connection.

It will commit the transaction automatically if callable_func does not
    raise exceptions. Otherwise, the transaction will be rolled back.

The intended use is to run multiple database queries concurrently.

example of use:
```python
await asyncio.gather(
    your_function_with_db_session(...), 
    run_in_new_ctx(
        your_function_with_db_session, some_arg, some_kwarg=123,
    ),
    run_in_new_ctx(your_function_with_db_session, ...),
)
```


## Testing

You can read more about testing here: [Testing](testing.md)

### rollback_session
```python
@asynccontextmanager
async def rollback_session(
    connection: DBConnect,
) -> AsyncGenerator[AsyncSession, None]:
```
A context manager that creates a session which is automatically rolled
back at the end.
It’s intended for use in fixtures to execute SQL queries during tests.

---

### set_test_context
```python
@asynccontextmanager
async def set_test_context(auto_close: bool = False) -> AsyncGenerator[None, None]:
```
A context manager that creates a new context in which you can place a
dedicated test session.
It’s intended for use in tests where the test and the application share
a single transaction.

Use `auto_close=False` if you’re using a test session and transaction
that you close elsewhere in your code.

Use `auto_close=True` if you want to call a function
in a test that uses a context while the middleware is not
active, and you want all sessions to be closed automatically.

---

### put_savepoint_session_in_ctx
```python
async def put_savepoint_session_in_ctx(
    connection: DBConnect,
    session: AsyncSession,
) -> AsyncGenerator[None, None]:
```
Sets the context to a session that uses a save point instead of creating
        a transaction. You need to pass the session you're using inside
        your tests to attach a new session to the same connection.

    It is important to use this function inside set_test_context.
