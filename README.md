# context-async-sqlalchemy

[![PyPI](https://img.shields.io/pypi/v/context-async-sqlalchemy.svg)](https://pypi.org/project/context-async-sqlalchemy/)


ContextVar + async sqlalchemy = happiness.

A convenient way to configure and interact with async sqlalchemy session
    through context in asynchronous applications.

## What does usage look like?

```python
from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from ..models import ExampleTable

async def some_func() -> None:
    # Created a session (no connection to the database yet)
    # If you call db_session again, it will return the same session
    # even in child coroutines.
    session = await db_session()
    
    stmt = insert(ExampleTable).values(text="example_with_db_session")

    # On the first request, a connection and transaction were opened
    await session.execute(stmt)

    # The commit and closing of the session will occur automatically
```


## How to use

The repository includes na example integration with FastAPI,
which describes numerous workflows.
[FastAPI example](https://github.com/krylosov-aa/context-async-sqlalchemy/tree/main/exmaples/fastapi_example/routes)


It also includes two types of test setups you can use in your projects.

[FastAPI tests example](https://github.com/krylosov-aa/context-async-sqlalchemy/tree/main/exmaples/fastapi_example/tests)

### The most basic example

#### 1. Configure the connection to the database

for example for PostgreSQL:

```python
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from context_async_sqlalchemy import db_connect

db_connect.engine = create_async_engine(
    f"postgresql+asyncpg://"
    f"{pg_user}:{pg_password}"
    f"@{host}:{pg_port}"
    f"/{pg_db}",
    future=True,
    pool_pre_ping=True,
)
db_connect.session_maker = async_sessionmaker(
    db_connect.engine, class_=AsyncSession, expire_on_commit=False
)

```

#### 2. Close the resources at the end of your application's life

Example for FastAPI:

```python
import asyncio
from typing import Any, AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from context_async_sqlalchemy import db_connect

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """
    It is important to clean up resources at the end of an application's
        life.
    """
    yield
    await asyncio.gather(
        db_connect.close(),  # Close the engine if it was open
        ...  # other resources in your application
    )
```


#### 3. Setup context lifetime

For a contextual session to work, a context needs to be set. This assumes some
kind of middleware.

I'll use FastAPI middleware as an example:
```python
from fastapi import Request
from starlette.middleware.base import (  # type: ignore[attr-defined]
    Response,
    RequestResponseEndpoint,
)

from context_async_sqlalchemy import (
    auto_commit_by_status_code,
    init_db_session_ctx,
    is_context_initiated,
    reset_db_session_ctx,
    rollback_db_session,
)


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
    # Tests may have different session management rules
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
```


You can use ready-made FastAPI middleware:
```python
from context_async_sqlalchemy import fastapi_db_session_middleware
from starlette.middleware.base import BaseHTTPMiddleware

app.add_middleware(
    BaseHTTPMiddleware, dispatch=fastapi_db_session_middleware
)
```


#### 4. Write a function that will work with the session

```python
from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from ..models import ExampleTable

async def handler_with_db_session() -> None:
    """
    An example of a typical handle that uses a context session to work with
        a database.
    Autocommit or autorollback occurs automatically at the end of a request
        (in middleware).
    """
    # Created a session (no connection to the database yet)
    # If you call db_session again, it will return the same session
    # even in child coroutines.
    session = await db_session()

    stmt = insert(ExampleTable).values(text="example_with_db_session")

    # On the first request, a connection and transaction were opened
    await session.execute(stmt)
```
