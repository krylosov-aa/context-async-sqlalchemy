from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from examples.database import connection
from examples.models import ExampleTable


async def auto_rollback_by_exception() -> None:
    """
    let's imagine that an exception occurred.
    """
    session = await db_session(connection)
    stmt = insert(ExampleTable)
    await session.execute(stmt)

    raise Exception("Some exception")
    # transaction will be automatically rolled back
