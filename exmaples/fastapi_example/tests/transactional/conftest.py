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

from context_async_sqlalchemy import (
    init_db_session_ctx,
    put_db_session_to_context,
    reset_db_session_ctx,
)


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
    put_db_session_to_context(db_session_test)
    try:
        yield
    finally:
        await reset_db_session_ctx(token)
