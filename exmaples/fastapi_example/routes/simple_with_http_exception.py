from fastapi import HTTPException

from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from ..models import ExampleTable


async def handler_with_db_session_and_http_exception() -> None:
    """
    let's imagine that an http exception occurred.
    """
    session = await db_session()
    stmt = insert(ExampleTable).values(text="example_with_db_session")
    await session.execute(stmt)
    raise HTTPException(status_code=500)
    # the transaction will be automatically rolled back in the middleware by
    #   status code
