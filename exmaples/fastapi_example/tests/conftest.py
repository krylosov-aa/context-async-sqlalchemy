"""
Basic settings and fixtures for testing
"""

from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from context_async_sqlalchemy import master_connect, replica_connect
from exmaples.fastapi_example.database import (
    create_engine,
    create_session_maker,
)
from exmaples.fastapi_example.setup_app import lifespan, setup_app


@pytest_asyncio.fixture
async def app() -> AsyncGenerator[FastAPI]:
    """
    A new application for each test allows for complete isolation between
        tests.
    """
    app = setup_app()
    async with lifespan(app):
        yield app


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
    engine = create_engine("127.0.0.1")
    session_maker = create_session_maker(engine)
    yield session_maker
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def close_connect() -> AsyncGenerator[None]:
    yield
    await master_connect.close()
    await replica_connect.close()
