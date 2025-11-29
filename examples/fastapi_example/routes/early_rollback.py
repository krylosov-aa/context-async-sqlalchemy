from context_async_sqlalchemy import db_session, rollback_db_session
from sqlalchemy import insert

from examples.database import connection
from examples.models import ExampleTable


async def early_rollback() -> None:
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
    stmt = insert(ExampleTable)
    await session.execute(stmt)
