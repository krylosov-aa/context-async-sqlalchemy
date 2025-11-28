from context_async_sqlalchemy import atomic_db_session, db_session
from sqlalchemy import insert

from ..database import connection
from ..models import ExampleTable


async def handler_with_db_session_and_atomic_2() -> None:
    """
    Let's imagine you already have a function that works with a contextual
    session, and its use case calls autocommit at the end of the request.
    You want to reuse this function, but you need to commit immediately,
        rather than wait for the request to complete.
    """
    # Open transaction
    await _insert_1()

    # autocommit current -> start and end new
    async with atomic_db_session(connection):
        await _insert_1()

    # Open transaction
    await _insert_1()

    # rollback current -> start and end new
    async with atomic_db_session(connection, "rollback"):
        await _insert_1()

    # Open transaction
    await _insert_1()

    # use current transaction and commit
    async with atomic_db_session(connection, "append"):
        await _insert_1()

    # Open transaction
    await _insert_1()

    # raise InvalidRequestError error
    async with atomic_db_session(connection, "raise"):
        await _insert_1()


async def _insert_1() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(
        text="example_with_db_session_and_atomic"
    )
    await session.execute(stmt)
