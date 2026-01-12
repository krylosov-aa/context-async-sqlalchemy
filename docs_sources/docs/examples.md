# Usage examples

You can see not only fragments of examples, but also
[web application examples](https://github.com/krylosov-aa/context-async-sqlalchemy/tree/main/examples).



### Basic usage

```python
from sqlalchemy import insert

from context_async_sqlalchemy import db_session

from ..database import connection
from ..models import ExampleTable


async def handler_with_db_session() -> None:
    """
    A typical handle that uses a context session to work with
        a database.
    Autocommit or autorollback occurs automatically at the end of a request
        in middleware.
    """
    # Creates a session with no connection to the database yet
    # If you call db_session again, it returns the same session
    # even in child coroutines.
    session = await db_session(connection)

    stmt = insert(ExampleTable).values(text="example_with_db_session")

    # On the first request, a connection and transaction are opened
    await session.execute(stmt)

    # Commits automatically
```

### Atomic

```python
from context_async_sqlalchemy import atomic_db_session, db_session
from sqlalchemy import insert

from ..database import connection
from ..models import ExampleTable


async def handler_with_db_session_and_atomic() -> None:
    """
    You have a function that works with a contextual
    session, and its use case calls autocommit at the end of the request.
    You want to reuse this function, but you need to commit immediately,
        instead of wait for the request to complete.
    """
    # the transaction commits or rolls back automatically
    # using the context manager
    async with atomic_db_session(connection):
        await _insert_1()

    # a new transaction in the same connection
    await _insert_1()


async def _insert_1() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(
        text="example_with_db_session_and_atomic"
    )
    await session.execute(stmt)
```

### Manually close the transaction and session

```python
from context_async_sqlalchemy import (
    close_db_session,
    commit_db_session,
    db_session,
)
from sqlalchemy import insert

from ..database import connection
from ..models import ExampleTable


async def handler_with_db_session_and_manual_close() -> None:
    """
    An example of a handle that uses a session in context,
    but commits manually and closes the session to release the connection.
    """
    # new connect -> new transaction -> commit
    await _insert_1()
    # old connect -> new transaction -> commit -> close connect
    await _insert_2()
    # new connect -> new transaction
    await _insert_3()
    # same connect -> same transaction
    await _insert_3()
    # autocommit


async def _insert_1() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(
        text="example_with_db_session_and_manual_close"
    )
    await session.execute(stmt)

    # We closed the transaction
    await session.commit()  # or await commit_db_session()


async def _insert_2() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(
        text="example_with_db_session_and_manual_close"
    )
    await session.execute(stmt)

    # We closed the transaction
    await commit_db_session(connection)

    # We closed the session, which returned the connection to the pool automatically.
    # Use if you have more work you need to complete without keeping the connection open.
    await close_db_session(connection)


async def _insert_3() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(
        text="example_with_db_session_and_manual_close"
    )
    await session.execute(stmt)
```

## Multiple sessions and concurrent execution

```python
import asyncio

from context_async_sqlalchemy import (
    close_db_session,
    commit_db_session,
    db_session,
    new_non_ctx_atomic_session,
    new_non_ctx_session,
    run_in_new_ctx,
)
from sqlalchemy import insert

from ..database import connection
from ..models import ExampleTable


async def handler_multiple_sessions() -> None:
    """
    You may need to run multiple sessions. For example, to run several queries concurrently.

    You can also use the same techniques to create new sessions whenever you
        need them, not necessarily because of the concurrent processing.
    """
    await asyncio.gather(
        _insert(),  # context session
        run_in_new_ctx(_insert),  # new context and session with autocommit
        run_in_new_ctx(  # new context and session with manual commit
            _insert_manual, "example_multiple_sessions",
        ),
        _insert_non_ctx(),  # new non context session
        _insert_non_ctx_manual(),  # new non context session
    )


async def _insert() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(text="example_multiple_sessions")
    await session.execute(stmt)


async def _insert_manual(text: str) -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(text=text)
    await session.execute(stmt)

    # manually commits the transaction (optional)
    await commit_db_session(connection)

    # manually closes the session (optional)
    await close_db_session(connection)


async def _insert_non_ctx() -> None:
    """
    Using context to work with sessions is optional.
    """
    async with new_non_ctx_atomic_session(connection) as session:
        stmt = insert(ExampleTable).values(text="example_multiple_sessions")
        await session.execute(stmt)


async def _insert_non_ctx_manual() -> None:
    """
    Using context to work with sessions is optional.
    """
    async with new_non_ctx_session(connection) as session:
        stmt = insert(ExampleTable).values(text="example_multiple_sessions")
        await session.execute(stmt)
        await session.commit()
```

### Rollback

```python
from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from ..database import connection
from ..models import ExampleTable


async def handler_with_db_session_and_exception() -> None:
    """
    let's imagine that an exception occurred.
    """
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(text="example_with_db_session")
    await session.execute(stmt)

    raise Exception("Some exception")
    # transaction automatically rolls back
```

```python
from fastapi import HTTPException

from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from ..database import connection
from ..models import ExampleTable


async def handler_with_db_session_and_http_exception() -> None:
    """
    let's imagine that an http exception occurred.
    """
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(text="example_with_db_session")
    await session.execute(stmt)

    raise HTTPException(status_code=500)
    # transaction rolls back automatically by status code
```

```python
from context_async_sqlalchemy import db_session, rollback_db_session
from sqlalchemy import insert

from ..database import connection
from ..models import ExampleTable


async def handler_with_db_session_and_manual_rollback() -> None:
    """
    An example of a handle that uses a rollback
    """
    # it's convenient this way
    await _insert()
    await rollback_db_session(connection)

    # but it's possible this way too
    await _insert()
    session = await db_session(connection)
    await session.rollback()


async def _insert() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(
        text="example_with_db_session_and_manual_close"
    )
    await session.execute(stmt)
```
