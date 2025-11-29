from sqlalchemy import insert

from context_async_sqlalchemy import db_session

from examples.database import connection
from examples.models import ExampleTable


async def simple_usage() -> None:
    """
    An example of a typical handle that uses a context session to work with
        a database.
    Autocommit or autorollback occurs automatically at the end of a request
        (in middleware).
    """
    # Created a session (no connection to the database yet)
    # If you call db_session again, it will return the same session
    # even in child coroutines.
    session = await db_session(connection)

    stmt = insert(ExampleTable)

    # On the first request, a connection and transaction were opened
    await session.execute(stmt)

    # Commit will happen automatically
