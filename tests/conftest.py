"""
Basic settings and fixtures for testing
"""

from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from context_async_sqlalchemy.test_utils import rollback_session
from examples.database import connection


@pytest_asyncio.fixture
async def db_session_test() -> AsyncGenerator[AsyncSession, None]:
    """The session that is used inside the test"""
    async with rollback_session(connection) as session:
        yield session
