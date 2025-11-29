from starlette.requests import Request
from starlette.exceptions import HTTPException

from context_async_sqlalchemy import db_session
from sqlalchemy import insert

from examples.database import connection
from examples.models import ExampleTable


async def auto_rollback_by_status_code(_: Request) -> None:
    """
    let's imagine that an error code was returned.
    """
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(text="example_with_db_session")
    await session.execute(stmt)

    raise HTTPException(status_code=500)
    # transaction will be automatically rolled back by status code
