"""
Basic settings and fixtures for testing
"""

from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import func, Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from context_async_sqlalchemy.test_utils import rollback_session
from examples.database import connection
from examples.models import ExampleTable
from ..setup_app import lifespan, setup_app


@pytest_asyncio.fixture
async def app() -> AsyncGenerator[FastAPI, None]:
    """
    A new application for each test allows for complete isolation between
        tests.
    """
    app = setup_app()
    async with lifespan(app):
        yield app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Client for calling application handlers"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def db_session_test() -> AsyncGenerator[AsyncSession, None]:
    """The session that is used inside the test"""
    async with rollback_session(connection) as session:
        yield session


async def count_rows_example_table(session: AsyncSession) -> int:
    result: Result[tuple[int]] = await session.execute(
        select(func.count()).select_from(ExampleTable)
    )
    return result.scalar_one()
