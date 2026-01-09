from context_async_sqlalchemy import (
    close_db_session,
    commit_db_session,
    db_session,
)
from sqlalchemy import insert

from examples.database import connection
from examples.models import ExampleTable


async def early_commit() -> None:
    """
    A handle that uses a session in context,
        but commits manually and  the session to release the
        connection.
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
    stmt = insert(ExampleTable)
    await session.execute(stmt)

    # We closed the transaction
    await session.commit()  # or await commit_db_session()


async def _insert_2() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable)
    await session.execute(stmt)

    # We closed the transaction
    await commit_db_session(connection)

    # We closed the session and returned the connection to the pool
    # Use if you have more work you need to complete without keeping the connection open.
    await close_db_session(connection)


async def _insert_3() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable)
    await session.execute(stmt)
