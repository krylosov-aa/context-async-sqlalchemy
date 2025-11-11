from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .connect import master_connect
from .context import (
    AsyncCallable,
    AsyncCallableResult,
    get_db_session_from_context,
    pop_db_session_from_context,
    put_db_session_to_context,
    run_in_new_ctx,
)


async def db_session() -> AsyncSession:
    """
    Get or initialize a context session with the database

    example of use:
        session = await db_session()
        ...
    """
    session = get_db_session_from_context()
    if not session:
        session = await master_connect.create_session()
        put_db_session_to_context(session)
    return session


@asynccontextmanager
async def atomic_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Autocommit or autorollback in place to avoid waiting for the end of the
        request.

    example of use:
        async with atomic_db_session()
            session = await db_session()  or your function that uses db_session
            ...
    """
    session = await db_session()
    async with session.begin():
        yield session


async def run_with_new_atomic_db_session(
    callable_func: AsyncCallable[AsyncCallableResult],
    *args: Any,
    **kwargs: Any,
) -> AsyncCallableResult:
    """
    Runs a function in a new context with a new session that has its
        own connection and transaction.
    The intended use is to run multiple database queries concurrently.

    example of use:
        await asyncio.gather(
          run_with_new_atomic_db_session(your_function_with_db_session, ...),
          run_with_new_atomic_db_session(your_function_with_db_session, ...),
        )
    """
    return await run_in_new_ctx(
        _atomic_wrapper, callable_func, *args, **kwargs
    )


async def run_with_new_db_session(
    callable_func: AsyncCallable[AsyncCallableResult],
    *args: Any,
    **kwargs: Any,
) -> AsyncCallableResult:
    """
    Runs a function in a new context with a new session that has its
        own connection.
    The intended use is to run multiple database queries concurrently.

    example of use:
        await asyncio.gather(
          run_with_new_atomic_db_session(your_function_with_db_session, ...),
          run_with_new_atomic_db_session(your_function_with_db_session, ...),
        )
    """
    return await run_in_new_ctx(callable_func, *args, **kwargs)


async def commit_db_session() -> None:
    """
    Commits the active session, if there is one.

    example of use:
        await your_function_with_db_session()
        await commit_db_session()
    """
    session = get_db_session_from_context()
    if session and session.in_transaction():
        await session.commit()


async def rollback_db_session() -> None:
    """
    Rollbacks the active session, if there is one.

    example of use:
        await your_function_with_db_session()
        await rollback_db_session()
    """
    session = get_db_session_from_context()
    if session and session.in_transaction():
        await session.rollback()


async def close_db_session() -> None:
    """
    Closes the active session (and connection), if there is one.

    This is useful if, for example, at the beginning of the handle a
        database query is needed, and then there is some other long-term work
        and you don't want to keep the connection opened.

    example of use:
        await your_function_with_db_session()
        await close_db_session()
    """
    session = pop_db_session_from_context()
    if session:
        await session.close()


@asynccontextmanager
async def new_non_ctx_session() -> AsyncGenerator[AsyncSession, None]:
    """Creating a new session without using a context"""
    session_maker = await master_connect.get_session_maker()
    async with session_maker() as session:
        yield session


@asynccontextmanager
async def new_non_ctx_atomic_session() -> AsyncGenerator[AsyncSession, None]:
    """Creating a new session with transaction without using a context"""
    async with new_non_ctx_session() as session:
        async with session.begin():
            yield session


async def _atomic_wrapper(
    callable_func: AsyncCallable[AsyncCallableResult],
    *args: Any,
    **kwargs: Any,
) -> AsyncCallableResult:
    async with atomic_db_session():
        return await callable_func(*args, **kwargs)
