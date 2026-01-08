import asyncio
from starlette.requests import Request
from starlette.responses import JSONResponse
from context_async_sqlalchemy import (
    close_db_session,
    commit_db_session,
    db_session,
    new_non_ctx_atomic_session,
    new_non_ctx_session,
    run_in_new_ctx,
)
from sqlalchemy import insert

from examples.database import connection
from examples.models import ExampleTable


async def concurrent_queries(_: Request) -> JSONResponse:
    """
    You may need to run multiple sessions simultaneously For example, to run several queries concurrently.

    You can also use these same techniques to create new sessions whenever you
        need them. Not necessarily just because of the concurrent processing.
    """
    await asyncio.gather(
        _insert(),  # context session
        run_in_new_ctx(_insert),  # new context and session with autocommit
        run_in_new_ctx(  # new context and session with manual commit
            _insert_manual,
            "example_multiple_sessions",
        ),
        _insert_non_ctx(),  # new non context session
        _insert_non_ctx_manual(),  # new non context session
        run_in_new_ctx(  # new context and session with autorollback
            _insert_with_exception
        ),
        return_exceptions=True,
    )
    return JSONResponse({})


async def _insert() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable)
    await session.execute(stmt)


async def _insert_manual(text: str) -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable).values(text=text)
    await session.execute(stmt)

    # commits the transaction (optional)
    await commit_db_session(connection)

    # manually closes the session (optional)
    await close_db_session(connection)


async def _insert_non_ctx() -> None:
    """
    While working with sessions, using context is optional
    """
    async with new_non_ctx_atomic_session(connection) as session:
        stmt = insert(ExampleTable)
        await session.execute(stmt)


async def _insert_non_ctx_manual() -> None:
    """
    While working with sessions, using context is optional
    """
    async with new_non_ctx_session(connection) as session:
        stmt = insert(ExampleTable)
        await session.execute(stmt)
        await session.commit()


async def _insert_with_exception() -> None:
    session = await db_session(connection)
    stmt = insert(ExampleTable)
    await session.execute(stmt)
    raise Exception()
