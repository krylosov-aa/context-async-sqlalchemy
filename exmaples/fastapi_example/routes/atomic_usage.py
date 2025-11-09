from context_async_sqlalchemy import atomic_db_session, db_session
from sqlalchemy import insert

from ..models import ExampleTable


async def handler_with_db_session_and_atomic() -> None:
    """
    Let's imagine you already have a function that works with a contextual
    session, and its use case calls autocommit at the end of the request.
    You want to reuse this function, but you need to commit immediately,
        rather than wait for the request to complete.
    """
    # the transaction will be committed or rolled back automatically
    # using the context manager
    async with atomic_db_session():
        await _insert_1()


async def _insert_1() -> None:
    session = await db_session()
    stmt = insert(ExampleTable).values(
        text="example_with_db_session_and_atomic"
    )
    await session.execute(stmt)
