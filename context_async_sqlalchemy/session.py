from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .connect import DBConnect
from .context import (
    get_db_session_from_context,
    pop_db_session_from_context,
    put_db_session_to_context,
)


async def db_session(connect: DBConnect) -> AsyncSession:
    """
    Get or initialize a context session with the database

    example of use:
        session = await db_session(connect)
        ...
    """
    session = get_db_session_from_context(connect.context_key)
    if not session:
        session = await connect.create_session()
        put_db_session_to_context(connect.context_key, session)
    return session


@asynccontextmanager
async def atomic_db_session(
    connect: DBConnect,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Autocommit or autorollback in place to avoid waiting for the end of the
        request.

    example of use:
        async with atomic_db_session(connect) as session
            await your_function_with_db_session()
            # also you can
            await session.execute(...)
    """
    session = await db_session(connect)
    async with session.begin():
        yield session


async def commit_db_session(connect: DBConnect) -> None:
    """
    Commits the active session, if there is one.

    example of use:
        await your_function_with_db_session()
        await commit_db_session(connect)
    """
    session = get_db_session_from_context(connect.context_key)
    if session and session.in_transaction():
        await session.commit()


async def rollback_db_session(connect: DBConnect) -> None:
    """
    Rollbacks the active session, if there is one.

    example of use:
        await your_function_with_db_session()
        await rollback_db_session(connect)
    """
    session = get_db_session_from_context(connect.context_key)
    if session and session.in_transaction():
        await session.rollback()


async def close_db_session(connect: DBConnect) -> None:
    """
    Closes the active session (and connection), if there is one.

    This is useful if, for example, at the beginning of the handle a
        database query is needed, and then there is some other long-term work
        and you don't want to keep the connection opened.

    example of use:
        await your_function_with_db_session()
        await close_db_session(connect)
    """
    session = pop_db_session_from_context(connect.context_key)
    if session:
        await session.close()


@asynccontextmanager
async def new_non_ctx_session(
    connect: DBConnect,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Creating a new session without using a context

    example of use:
        async with new_non_ctx_session(connect) as session:
            await session.execute(...)
    """
    session_maker = await connect.get_session_maker()
    async with session_maker() as session:
        yield session


@asynccontextmanager
async def new_non_ctx_atomic_session(
    connect: DBConnect,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Creating a new session with transaction without using a context

    example of use:
        async with new_non_ctx_atomic_session(connect) as session:
            await session.execute(...)
    """
    async with new_non_ctx_session(connect) as session:
        async with session.begin():
            yield session
