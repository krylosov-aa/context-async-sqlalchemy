from context_async_sqlalchemy import db_session, rollback_db_session
from sqlalchemy import insert

from ..models import ExampleTable


async def handler_with_db_session_and_manual_rollback() -> None:
    """
    An example of a handle that uses a rollback
    """
    # it's convenient this way
    await _insert()
    await rollback_db_session()

    # but it's possible this way too
    await _insert()
    session = await db_session()
    await session.rollback()


async def _insert() -> None:
    session = await db_session()
    stmt = insert(ExampleTable).values(
        text="example_with_db_session_and_manual_close"
    )
    await session.execute(stmt)
