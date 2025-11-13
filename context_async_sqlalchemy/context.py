from contextvars import ContextVar, copy_context, Token
from typing import Any, Awaitable, Callable, Generator, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession


def init_db_session_ctx() -> Token[dict[str, AsyncSession] | None]:
    """
    Initiates a context for storing sessions
    """
    if is_context_initiated():
        raise Exception("Context already initiated")

    return _init_db_session_ctx()


def is_context_initiated() -> bool:
    """
    Checks whether the context is initiated
    """
    return bool(_db_session_ctx.get())


def pop_db_session_from_context(context_key: str) -> AsyncSession | None:
    """
    Removes a session from the context
    """
    session_ctx = _db_session_ctx.get()
    if not session_ctx:
        return None

    session: AsyncSession | None = session_ctx.pop(context_key, None)
    return session


async def reset_db_session_ctx(
    token: Token[dict[str, AsyncSession] | None], with_close: bool = True
) -> None:
    """
    Removes sessions from the context and also closes the session if it
        is open.
    """
    if with_close:
        for session in sessions_stream():
            await session.close()
    _db_session_ctx.reset(token)


def get_db_session_from_context(context_key: str) -> AsyncSession | None:
    """
    Extracts the session from the context
    """
    session_ctx = _get_initiated_context()
    return session_ctx.get(context_key)


def put_db_session_to_context(
    context_key: str,
    session: AsyncSession,
) -> None:
    """
    Puts the session into context
    """
    session_ctx = _get_initiated_context()
    session_ctx[context_key] = session


def sessions_stream() -> Generator[AsyncSession, Any, None]:
    """Read all open context sessions"""
    for session in _get_initiated_context().values():
        yield session


AsyncCallableResult = TypeVar("AsyncCallableResult")
AsyncCallable = Callable[..., Awaitable[AsyncCallableResult]]


async def run_in_new_ctx(
    callable_func: AsyncCallable[AsyncCallableResult],
    *args: Any,
    **kwargs: Any,
) -> AsyncCallableResult:
    """
    Runs a function in a new context with new sessions that have their
        own connection.
    The intended use is to run multiple database queries concurrently.

    example of use:
        await asyncio.gather(
          run_in_new_ctx(your_function_with_db_session, ...),
          run_in_new_ctx(your_function_with_db_session, ...),
        )
    """
    new_ctx = copy_context()
    return await new_ctx.run(_new_ctx_wrapper, callable_func, *args, **kwargs)


_db_session_ctx: ContextVar[dict[str, AsyncSession] | None] = ContextVar(
    "db_session_ctx", default=None
)


def _get_initiated_context() -> dict[str, AsyncSession]:
    session_ctx = _db_session_ctx.get()
    if session_ctx is None:
        raise Exception("Context is not initiated")
    return session_ctx


def _init_db_session_ctx() -> Token[dict[str, AsyncSession] | None]:
    session_ctx: dict[str, AsyncSession] | None = {}
    return _db_session_ctx.set(session_ctx)


async def _new_ctx_wrapper(
    callable_func: AsyncCallable[AsyncCallableResult],
    *args: Any,
    **kwargs: Any,
) -> AsyncCallableResult:
    token = init_db_session_ctx()
    try:
        return await callable_func(*args, **kwargs)
    finally:
        await reset_db_session_ctx(token)
