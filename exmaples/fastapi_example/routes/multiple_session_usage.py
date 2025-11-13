import asyncio

from context_async_sqlalchemy import (
    atomic_db_session,
    close_db_session,
    commit_db_session,
    db_session,
    run_in_new_ctx,
)
from sqlalchemy import insert

from ..database import master
from ..models import ExampleTable


async def handler_multiple_sessions() -> None:
    """
    In some situations, you need to have multiple sessions running
        simultaneously. For example, to run several queries concurrently.
    """
    await asyncio.gather(
        run_in_new_ctx(_insert),
        run_in_new_ctx(_insert_manual),
        run_in_new_ctx(_insert),
        run_in_new_ctx(_insert_manual),
        run_in_new_ctx(_insert),
    )


async def _insert() -> None:
    async with atomic_db_session(master) as session:
        stmt = insert(ExampleTable).values(text="example_multiple_sessions")
        await session.execute(stmt)


async def _insert_manual() -> None:
    session = await db_session(master)
    stmt = insert(ExampleTable).values(text="example_multiple_sessions")
    await session.execute(stmt)
    await commit_db_session(master)

    # You can manually close the session if you want, but it is not necessary
    await close_db_session(master)
