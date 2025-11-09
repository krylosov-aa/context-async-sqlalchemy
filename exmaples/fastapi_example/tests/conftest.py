"""
Basic settings and fixtures for testing
"""

from typing import AsyncGenerator, Generator

import pytest_asyncio
import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from exmaples.fastapi_example.database import (
    create_engine,
    create_session_maker,
)
from exmaples.fastapi_example.setup_app import setup_app


@pytest.fixture
def app() -> Generator[FastAPI]:
    """
    A new application for each test allows for complete isolation between
        tests.
    """
    yield setup_app()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient]:
    """Client for calling application handlers"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


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


@pytest_asyncio.fixture
async def session_maker_test() -> AsyncGenerator[
    async_sessionmaker[AsyncSession]
]:
    engine = create_engine()
    session_maker = create_session_maker(engine)
    yield session_maker
    await engine.dispose()
