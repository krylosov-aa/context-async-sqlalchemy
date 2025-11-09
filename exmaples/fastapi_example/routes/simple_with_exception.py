from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from ..models import ExampleTable


async def handler_with_db_session_and_exception() -> None:
    """
    let's imagine that an exception occurred.
    """
    session = await db_session()
    stmt = insert(ExampleTable).values(text="example_with_db_session")
    await session.execute(stmt)
    raise Exception("Some exception")
    # the transaction will be automatically rolled back in the middleware
