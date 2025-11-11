"""
Fair tests in which the application manages the session lifecycle itself.
Data isolation between tests is performed by running trunks before and after
    each test.
This is fair testing, but slower.
"""

from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy import text
from exmaples.fastapi_example.database import (
    create_engine,
    create_session_maker,
)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_tables_after() -> AsyncGenerator[None]:
    """
    After each test, we delete all data from the tables to isolate the data.
    We always clear the data after each test to avoid interfering with
        transactional tests.

    We don't use a shared transaction per test to ensure fair testing of the
    application and that it works correctly with sessions and transactions.

    This also makes debugging tests easier, as you can connect to the
        database and view committed changes.

    The downside is that tests will run slower, and you can't simply
        start multiple workers because the database is shared and will
        be cleared at a random time for other tests.

    If multiple workers are required, you need to set up a separate
        database for each worker.
    """
    yield
    await _cleanup_tables()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def cleanup_tables_before() -> None:
    """
    Clears data once before running all tests.
    This is for cases where a test is interrupted (for example, when
        using the debugger) and cleanup_tables_after is not executed.

    It has its own engine, since the scope is session.
    """
    await _cleanup_tables()


async def _cleanup_tables() -> None:
    engine = create_engine("127.0.0.1")
    session_maker = create_session_maker(engine)
    async with session_maker() as session:
        await session.execute(
            text("TRUNCATE TABLE example RESTART IDENTITY CASCADE;")
        )
        await session.commit()
    await engine.dispose()
