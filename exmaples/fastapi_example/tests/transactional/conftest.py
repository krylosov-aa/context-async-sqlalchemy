"""
An example of fast-running tests, as the transaction for both the test and
    the application is shared.
This allows data isolation to be achieved by rolling back the transaction
    rather than deleting data from tables.

It's not exactly fair testing, because the app doesn't manage the session
    itself.
But for most basic tests, it's sufficient.
On the plus side, these tests run faster.
"""

from typing import AsyncGenerator

import pytest_asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from exmaples.fastapi_example.database import master
from context_async_sqlalchemy import (
    init_db_session_ctx,
    put_db_session_to_context,
    reset_db_session_ctx,
)


@pytest_asyncio.fixture
async def db_session_test(
    session_maker_test: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    """The session that is used inside the test"""
    async with session_maker_test() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def db_session_override(
    db_session_test: AsyncSession,
) -> AsyncGenerator[None]:
    """
    The key thing about these tests is that we override the context in advance.
    The middleware has a special check that won't initialize the context
        if it already exists.
    """
    token = init_db_session_ctx()

    # Here we create a new session with save point behavior.
    # This means that committing within the application will save and
    #   release the save point, rather than committing the entire transaction.
    conn = await db_session_test.connection()
    new_session = AsyncSession(
        bind=conn, join_transaction_mode="create_savepoint"
    )
    put_db_session_to_context(master.context_key, new_session)
    try:
        yield
    finally:
        await reset_db_session_ctx(
            token,
            # Don't close the session here, as you opened in fixture.
            with_close=False,
        )
