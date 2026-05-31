from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import insert

from context_async_sqlalchemy import db_session
from examples.database import connection
from examples.models import ExampleTable


async def auto_rollback_by_status_code() -> None:
    """
    let's imagine that an error code was returned.
    """
    session = await db_session(connection)
    stmt = insert(ExampleTable)
    await session.execute(stmt)

    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    # transaction rolls back automatically by status code
