import asyncio

from context_async_sqlalchemy import (
    close_db_session,
    commit_db_session,
    db_session,
    run_with_new_atomic_db_session,
    run_with_new_db_session,
)
from sqlalchemy import insert

from ..models import ExampleTable


async def handler_multiple_sessions() -> None:
    """
    In some situations, you need to have multiple sessions running
        simultaneously. For example, to run several queries concurrently.
    """
    await asyncio.gather(
        run_with_new_atomic_db_session(_insert),
        run_with_new_db_session(_insert_manual),
        run_with_new_atomic_db_session(_insert),
        run_with_new_db_session(_insert_manual),
        run_with_new_atomic_db_session(_insert),
    )


async def _insert() -> None:
    session = await db_session()
    stmt = insert(ExampleTable).values(text="example_multiple_sessions")
    await session.execute(stmt)


async def _insert_manual() -> None:
    session = await db_session()
    stmt = insert(ExampleTable).values(text="example_multiple_sessions")
    await session.execute(stmt)
    await commit_db_session()

    # You can manually close the session if you want, but it is not necessary
    await close_db_session()
