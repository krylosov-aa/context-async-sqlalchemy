# Getting started

## Configure the connection to the database

For example, for PostgreSQL - database.py:

```python
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from context_async_sqlalchemy import DBConnect


def create_engine(host: str) -> AsyncEngine:
    """
    database connection parameters.
    """

    # In production code, you will probably take these parameters from env
    pg_user = "krylosov-aa"
    pg_password = ""
    pg_port = 6432
    pg_db = "test"
    return create_async_engine(
        f"postgresql+asyncpg://"
        f"{pg_user}:{pg_password}"
        f"@{host}:{pg_port}"
        f"/{pg_db}",
        future=True,
        pool_pre_ping=True,
    )


def create_session_maker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """session parameters"""
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


connection = DBConnect(
    engine_creator=create_engine,
    session_maker_creator=create_session_maker,
    host="127.0.0.1",  # optional
)
```

The **host** parameter is optional if you use a handler
before creating a session - `before_create_session_handler`.
In that case, you can dynamically set the host.

Read more in [Master/Replica or several databases at the same time](master_replica.md)


## Manage Database connection lifecycle

 
Close resources at the end of your application's lifecycle.

Example for FastAPI:

```python
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI

from database import connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """Database connection lifecycle management"""
    yield
    await connection.close()  # Close the engine if it was open
```

## Setup middleware

Middleware handles the most important and complex part -
managing context and sessions.

You can use the ready-made middleware components:

### Pure ASGI

```python
from context_async_sqlalchemy import ASGIHTTPDBSessionMiddleware

app.add_middleware(ASGIHTTPDBSessionMiddleware)
```

### FastAPI

```python
from context_async_sqlalchemy.fastapi_utils import (
    add_fastapi_http_db_session_middleware,
)

app = FastAPI(...)
add_fastapi_http_db_session_middleware(app)
```

### Starlette

```python
from context_async_sqlalchemy.starlette_utils import (
    add_starlette_http_db_session_middleware,
)

app = Starlette(...)
add_starlette_http_db_session_middleware(app)
```

### Write own

If there’s no ready-made solution that fits your needs - don’t worry!
You can check out [how it works](how_middleware_works.md) and implement your
own.


## Use it

```python
from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from database import connection  # your configured connection to the database
from models import ExampleTable  # just some model for example

async def some_func() -> None:
    # Created a session (no connection to the database yet)
    session = await db_session(connection)
    
    stmt = insert(ExampleTable).values(text="example_with_db_session")

    # On the first request, a connection and transaction were opened
    await session.execute(stmt)
    
    # If you call db_session again, it will return the same session
    # even in child coroutines.
    session = await db_session(connection)
    
    # The second request will use the same connection and the same transaction
    await session.execute(stmt)

    # The commit and closing of the session will occur automatically
```


## Examples

The repository includes an example integration with FastAPI, demonstrating
various workflows:
[FastAPI example](https://github.com/krylosov-aa/context-async-sqlalchemy/tree/main/examples/fastapi_example/routes)

It also contains two types of test setups that you can use in your own
projects.

All library tests are included within the examples - because we aim to
test the functionality not in isolation, but in the context of a real
asynchronous web application.
[FastAPI tests example](https://github.com/krylosov-aa/context-async-sqlalchemy/tree/main/examples/fastapi_example/tests)
