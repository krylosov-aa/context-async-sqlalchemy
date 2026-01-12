# Concurrent sql queries


Concurrent query execution deserves special attention.
In SQLAlchemy, you can’t run multiple queries concurrently within the same
session. You need to create a new one.

The library provides two simple ways to execute queries concurrently:

- Run a function in a new context: `run_in_new_ctx`
- Create a new session that is independent of the current context:
`new_non_ctx_atomic_session` or `new_non_ctx_session`


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
