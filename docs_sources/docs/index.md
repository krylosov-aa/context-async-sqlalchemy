# context-async-sqlalchemy

[![PyPI](https://img.shields.io/pypi/v/context-async-sqlalchemy.svg)](https://pypi.org/project/context-async-sqlalchemy/)

No AI was used in the creation of this library.

[SOURCE CODE](https://github.com/krylosov-aa/context-async-sqlalchemy)

Provides a super convenient way to work with SQLAlchemy in asynchronous
applications.
It handles the lifecycle management of the engine, sessions, and
transactions.

The main goal is to provide quick and easy access to a session,
without having to worry about opening or closing it when it’s not necessary.

Key features:

- Extremely easy to use
- Automatically manages the lifecycle of the engine, sessions, and
transactions (autocommit / autorollback)
- Does not interfere with manually opening or closing sessions and
transactions when needed
- Framework-agnostic - works with any web framework
- Not a wrapper around SQLAlchemy
- Convenient for testing
- Runtime host switching
- Supports multiple databases and multiple sessions per database
- Provides tools for running concurrent SQL queries
- Fully lazy initialization


## What does usage look like?

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

## How it works

Here is a very simplified diagram of how everything works:

![basic schema.png](img/basic_schema.png)

1. Before executing your code, the middleware will prepare a container in
which the sessions required by your code will be stored.
The container is saved in contextvars
2. Your code accesses the library to create new sessions and retrieve
existing ones
3. After your code, middleware will automatically commit or roll back open
transactions. Closes open sessions and clears the context.

The library also provides the ability to commit, rollback, and close at any
time, without waiting for the end of the request, without any problems.
