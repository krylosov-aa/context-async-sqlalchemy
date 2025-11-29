from starlette.requests import Request
from starlette.responses import JSONResponse
from context_async_sqlalchemy import (
    atomic_db_session,
    close_db_session,
    db_session,
)
from sqlalchemy import insert

from examples.database import connection
from examples.models import ExampleTable


async def early_connection_close(_: Request) -> JSONResponse:
    """
    An example when you can return a connection to the connection pool for a
        long period of work unrelated to the database
    """
    async with atomic_db_session(connection):
        await _insert()

    await close_db_session(connection)

    ...
    # There's a lot of work going on here.
    ...

    # new connect and new transaction
    await _insert()
    return JSONResponse({})


async def _insert() -> None:
    """
    Let's imagine that the same function is useful to us in another handle,
        where it is good to use it in a common transaction for the entire
        request.
    """
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(
        text="example_with_early_connection_close"
    )
    await session.execute(stmt)
