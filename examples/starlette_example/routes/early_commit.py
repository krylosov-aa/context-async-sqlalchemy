from starlette.requests import Request
from starlette.responses import JSONResponse
from context_async_sqlalchemy import (
    close_db_session,
    commit_db_session,
    db_session,
)
from sqlalchemy import insert

from examples.database import connection
from examples.models import ExampleTable


async def early_commit(_: Request) -> JSONResponse:
    """
    An example of a handle that uses a session in context,
        but commits manually and even closes the session to release the
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

    return JSONResponse({})
    # autocommit


async def _insert_1() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable)
    await session.execute(stmt)

    # Here we closed the transaction
    await session.commit()  # or await commit_db_session()


async def _insert_2() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable)
    await session.execute(stmt)

    # Here we closed the transaction
    await commit_db_session(connection)

    # And here we closed the session = returned the connection to the pool
    # This is useful if, for example, at the beginning of the handle a
    # database query is needed, and then there is some other long-term work
    # and you don't want to keep the connection opened.
    await close_db_session(connection)


async def _insert_3() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable)
    await session.execute(stmt)
