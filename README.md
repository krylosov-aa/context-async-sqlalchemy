# context-async-sqlalchemy

[![PyPI](https://img.shields.io/pypi/v/context-async-sqlalchemy.svg)](https://pypi.org/project/context-async-sqlalchemy/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/context-async-sqlalchemy?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/context-async-sqlalchemy)
[![Tests](https://github.com/krylosov-aa/context-async-sqlalchemy/actions/workflows/tests.yml/badge.svg)](https://github.com/krylosov-aa/context-async-sqlalchemy/actions/workflows/tests.yml) (coverage > 90%)

No AI was used in the creation of this library.

[DOCUMENTATION](https://krylosov-aa.github.io/context-async-sqlalchemy/)

Provides a super convenient way to work with SQLAlchemy in asynchronous
applications.
It handles the lifecycle management of the engine, sessions, and
transactions.

The main goal is to provide quick and easy access to a session,
without worrying about opening or closing it when it’s not necessary.

Key features:

- Automatically manages the lifecycle of the engine, sessions, and
transactions
- Allows for user autonomy when manually opening or closing sessions and
transactions
- Framework-agnostic
- Not a wrapper around SQLAlchemy
- Convenient for testing
- Runtime host switching
- Supports multiple databases and sessions per database
- Provides tools for running concurrent SQL queries
- Fully lazy initialization


## Example of a typical session

```python
from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from database import connection  # your configured connection to the database
from models import ExampleTable  # a model for example

async def some_func() -> None:
    # Creates a session with no connection to the database yet
    session = await db_session(connection)
    
    stmt = insert(ExampleTable).values(text="example_with_db_session")

    # A connection and transaction open in the first request.
    await session.execute(stmt)
    
    # If you call db_session again, it returns the same session
    # even in child coroutines.
    session = await db_session(connection)
    
    # The second request uses the same connection and the same transaction
    await session.execute(stmt)

    # The commit and closing of the session occurs automatically
```

## How it works

![basic schema.png](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/docs_sources/docs/img/basic_schema.png?raw=true)

1. Before executing your code, the middleware prepares a container in
which the sessions required by your code are stored.
The container is saved in `contextvars`.
2. Your code accesses the library to create new sessions and retrieve
existing ones.
3. The middleware automatically commits or rolls back open
transactions. It also closes open sessions and clears the context.

The library provides the ability to commit, roll back, and close at any
time without waiting for the end of the request.