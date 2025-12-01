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
from sqlalchemy.ext.asyncio import AsyncSession

from context_async_sqlalchemy.test_utils import (
    put_savepoint_session_in_ctx,
    set_test_context,
)
from examples.database import connection


@pytest_asyncio.fixture(autouse=True)
async def db_session_override(
    db_session_test: AsyncSession,
) -> AsyncGenerator[None, None]:
    """
    The key thing about these tests is that we override the context in advance.
    The middleware has a special check that won't initialize the context
        if it already exists.
    """
    async with set_test_context():
        async with put_savepoint_session_in_ctx(connection, db_session_test):
            yield
