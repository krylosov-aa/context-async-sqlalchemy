from context_async_sqlalchemy import atomic_db_session, db_session
from sqlalchemy import insert

from examples.database import connection
from examples.models import ExampleTable


async def atomic_and_previous_transaction() -> None:
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

    # use current transaction and rollback
    try:
        async with atomic_db_session(connection, "append"):
            await _insert_1()
            raise Exception()
    except Exception:
        ...

    # Open transaction
    await _insert_1()

    # raise InvalidRequestError error
    async with atomic_db_session(connection, "raise"):
        await _insert_1()


async def _insert_1() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values()
    await session.execute(stmt)
