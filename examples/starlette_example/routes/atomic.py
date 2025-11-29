from starlette.requests import Request
from starlette.responses import JSONResponse
from context_async_sqlalchemy import atomic_db_session, db_session
from sqlalchemy import insert

from examples.database import connection
from examples.models import ExampleTable


async def atomic_base_example(_: Request) -> JSONResponse:
    """
    Let's imagine you already have a function that works with a contextual
    session, and its use case calls autocommit at the end of the request.
    You want to reuse this function, but you need to commit immediately,
        rather than wait for the request to complete.
    """
    # the transaction will be committed or rolled back automatically
    # using the context manager
    async with atomic_db_session(connection):
        await _insert_1()

    # This is a new transaction in the same connection
    await _insert_1()

    return JSONResponse({})


async def _insert_1() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values()
    await session.execute(stmt)
