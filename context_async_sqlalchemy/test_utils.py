"""Utilities to use during testing"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from context_async_sqlalchemy import (
    DBConnect,
    init_db_session_ctx,
    put_db_session_to_context,
    reset_db_session_ctx,
)


@asynccontextmanager
async def rollback_session(
    connection: DBConnect,
) -> AsyncGenerator[AsyncSession]:
    """A session that always rolls back"""
    session_maker = await connection.get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()


@asynccontextmanager
async def set_test_context() -> AsyncGenerator[None]:
    """
    Opens a context similar to middleware, but doesn't commit or
        rollback automatically. This task falls to the fixture in tests.
    """
    token = init_db_session_ctx()
    try:
        yield
    finally:
        await reset_db_session_ctx(
            token,
            # Don't close the session here, as you opened in fixture.
            with_close=False,
        )


@asynccontextmanager
async def put_savepoint_session_in_ctx(
    connection: DBConnect,
    session: AsyncSession,
) -> AsyncGenerator[None]:
    """
    Sets the context to a session that uses a save point instead of creating
        a transaction. You need to pass the session you're using inside
        your tests to attach a new session to the same connection.

    It is also important to use this function inside set_test_context.
    """
    session_maker = await connection.get_session_maker()
    async with session_maker(
        # Bind to the same connection
        bind=await session.connection(),
        # Instead of opening a transaction, it creates a save point
        join_transaction_mode="create_savepoint",
    ) as session:
        put_db_session_to_context(connection, session)
    yield
