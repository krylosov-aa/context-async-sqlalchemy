"""
Here are the functions for implementing the "Read your own writes" pattern.
To implement it, we use LSN from the postgresql WAL log.
"""

from contextvars import ContextVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class _LsnHolder:
    """
    The holder is needed so that the nested context can update the lsn value,
        which will then be visible in the middleware context.
    """

    value: str | None = None


_request_lsn: ContextVar[_LsnHolder] = ContextVar("_request_lsn")


def get_request_lsn() -> _LsnHolder:
    """
    Retrieves the LSN from the context if there was a write transaction.
    """
    lsn_holder = _request_lsn.get()
    if lsn_holder is None:
        raise RuntimeError("Context with LSN holder is not initialized")

    return lsn_holder


async def save_current_lsn_if_there_writes(session: AsyncSession) -> None:
    """
    Saves the LSN to the context if there was a write transaction.
    """
    lsn = await get_current_lsn_if_there_writes(session)
    if lsn:
        lsn_holder = get_request_lsn()
        lsn_holder.value = lsn


async def get_current_lsn_if_there_writes(session: AsyncSession) -> str | None:
    """
    Returns the LSN if there was a write transaction.
    """
    # pg_current_xact_id_if_assigned() returns NULL if:
    #   - session contained only SELECT (XID is not assigned)
    #   - read-only session to replica
    result = await session.execute(
        text(
            "SELECT pg_current_wal_lsn()::text "
            "WHERE pg_current_xact_id_if_assigned() IS NOT NULL"
        )
    )
    return result.scalar()


async def lsn_cookie_middleware(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
    holder = _LsnHolder()
    _request_lsn.set(holder)

    response = await call_next(request)
    lsn_holder = get_request_lsn()
    if lsn_holder.value:
        response.headers["Set-Cookie"] = (
            f"X-WAL-LSN={lsn_holder.value}; Path=/; SameSite=Lax; Secure"
        )
    return response
