"""
Basic settings and fixtures for testing
"""

from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from exmaples.fastapi_example.database import master
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
async def session_maker_test(
    app: FastAPI,  # To make the connection to the database in lifespan
) -> AsyncGenerator[async_sessionmaker[AsyncSession]]:
    session_maker = await master.get_session_maker()
    yield session_maker
