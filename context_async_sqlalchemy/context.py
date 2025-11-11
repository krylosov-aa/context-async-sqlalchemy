from contextvars import ContextVar, copy_context, Token
from typing import Any, Awaitable, Callable, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from .connect import master_connect


def init_db_session_ctx() -> Token[dict[str, AsyncSession] | None]:
    """
    Initiates a context for storing the session
    """
    if is_context_initiated():
        raise Exception("Context already initiated")

    return _init_db_session_ctx()


def is_context_initiated() -> bool:
    """
    Checks whether the context is initiated
    """
    return bool(_db_session_ctx.get())


def pop_db_session_from_context() -> AsyncSession | None:
    """
    Removes a session from the context
    """
    session_ctx = _db_session_ctx.get()
    if not session_ctx:
        return None

    session: AsyncSession | None = session_ctx.pop("session", None)
    return session


async def reset_db_session_ctx(
    token: Token[dict[str, AsyncSession] | None],
) -> None:
    """
    Removes a session from the context and also closes the session if it
        is open.
    """
    session = pop_db_session_from_context()
    if session:
        await session.close()
    _db_session_ctx.reset(token)


def get_db_session_from_context() -> AsyncSession | None:
    """
    Extracts the session from the context
    """
    session_ctx = _get_initiated_context()
    return session_ctx.get("session")


def put_db_session_to_context(session: AsyncSession) -> None:
    """
    Puts the session into context
    """
    session_ctx = _get_initiated_context()
    session_ctx["session"] = session


AsyncCallableResult = TypeVar("AsyncCallableResult")
AsyncCallable = Callable[..., Awaitable[AsyncCallableResult]]


async def run_in_new_ctx(
    callable_func: AsyncCallable[AsyncCallableResult],
    *args: Any,
    **kwargs: Any,
) -> AsyncCallableResult:
    """
    Copies the context and initializes a new context for the new session,
        then runs the function in the new context.
    """
    new_ctx = copy_context()
    return await new_ctx.run(_new_ctx_wrapper, callable_func, *args, **kwargs)


def _get_initiated_context() -> dict[str, AsyncSession]:
    session_ctx = _db_session_ctx.get()
    if session_ctx is None:
        raise Exception("Context is not initiated")
    return session_ctx


_db_session_ctx: ContextVar[dict[str, AsyncSession] | None] = ContextVar(
    "db_session_ctx", default=None
)


def _init_db_session_ctx() -> Token[dict[str, AsyncSession] | None]:
    session_ctx: dict[str, AsyncSession] | None = {}
    return _db_session_ctx.set(session_ctx)


async def _new_ctx_wrapper(
    callable_func: AsyncCallable[AsyncCallableResult],
    *args: Any,
    **kwargs: Any,
) -> AsyncCallableResult:
    _init_db_session_ctx()
    session_maker = await master_connect.get_session_maker()
    async with session_maker() as session:
        put_db_session_to_context(session)
        return await callable_func(*args, **kwargs)
