# API Reference


## DBConnect

DBConnect is responsible for managing the engine and `session_maker`
You need to define two factories:

- Specify host to which you want to connect (optional).
- Specify a handler that runs before a session is created.
It will be used to connect to the host for the first time or to reconnect to a new one (optional).

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
It doesn’t need to be called explicitly.
If you don't use the call, the first session request will automatically
establishes the connection.

---

### change_host

```python
async def change_host(self: DBConnect, host: str) -> None:
```
Establishes a connection to the specified host. It then validates that the currently connected host is different
from the target host.

---

### create_session

```python
async def create_session(self: DBConnect) -> AsyncSession:
```
Creates a new session the library uses internally.
You never need to call it directly. (Only maybe in some special cases.)
---

### session_maker

```python
async def session_maker(self: DBConnect) -> async_sessionmaker[AsyncSession]:
```
Provides access to the `session_maker` currently used to create sessions.


---

### close

```python
async def close(self: DBConnect) -> None:
```
Closes and cleans up all resources, freeing the connection pool.
Use this call at the end of your application’s life cycle.



## Middlewares

Most of the work the “magic” happens inside the middleware. Check out
[how it works](how_middleware_works.md) and implement your own if the ready-made ones don't fit.

### FastAPI
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

Here are the library functions you will use most often.
They allow you to work with sessions directly from your asynchronous code.

### db_session
```python
async def db_session(connect: DBConnect) -> AsyncSession:
```
The most important function for obtaining a session in your code.
Returns a new session when you call it for the first time; subsequent
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
A context manager you can use to wrap another function which
uses a context session, making that call isolated within its own transaction.

Several options define how a function handles an open transaction.

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
Commits the active session.

---

### rollback_db_session
```python
async def rollback_db_session(connect: DBConnect) -> None:
```
Rolls back an active session.

---

### close_db_session
```python
async def close_db_session(connect: DBConnect) -> None:
```
Closes the current context session and returns the connection to the pool.
If you close an uncommitted transaction, the connection rolls back

This is useful when you need to run a database query at the start of the
handler, then continue working over time without keeping the connection open.

---

### new_non_ctx_session
```python
@asynccontextmanager
async def new_non_ctx_session(
    connect: DBConnect,
) -> AsyncGenerator[AsyncSession, None]:
```
A context manager that allows you to create a new session without
placing it in a context.

---

### new_non_ctx_atomic_session
```python
@asynccontextmanager
async def new_non_ctx_atomic_session(
    connect: DBConnect,
) -> AsyncGenerator[AsyncSession, None]:
```
Runs a function in a new context with new session(s) that have a separate connection.

It commits the transaction automatically if <code>callable_func</code> does not
raise exceptions. Otherwise, the transaction rolls back.

It is intended to allow you to run multiple database queries concurrently.


## Context

### run_in_new_ctx
```python
async def run_in_new_ctx(
    callable_func: AsyncCallable[AsyncCallableResult],
    *args: Any,
    **kwargs: Any,
) -> AsyncCallableResult:
```
Runs a function in a new context with new session(s) that have a
separate connection.

It commits the transaction automatically if `callable_func` does not
raise exceptions. Otherwise, the transaction rolls back.

It is intended to allow you to run multiple database queries concurrently.

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

### rollback_session
```python
@asynccontextmanager
async def rollback_session(
    connection: DBConnect,
) -> AsyncGenerator[AsyncSession, None]:
```
A context manager that creates a session which automatically rolls back at the end of the session.
It is intended for you to use in fixtures to execute SQL queries during tests.

---

### set_test_context
```python
@asynccontextmanager
async def set_test_context(auto_close: bool = False) -> AsyncGenerator[None, None]:
```
A context manager that creates a new context in which you can place a
dedicated test session.
It is intended to test the application when it shares a single transaction.

Use `auto_close=False` if you’re using a test session and transaction
that you close elsewhere in your code.

Use `auto_close=True` if you want to call a function
in a test that uses a context while the middleware is not
active. All sessions close automatically.

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

Learn more about [testing](testing.md)
