from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from context_async_sqlalchemy import (
    init_db_session_ctx,
    put_db_session_to_context,
    reset_db_session_ctx,
)
from context_async_sqlalchemy.auto_commit import (
    auto_commit_by_status_code,
    commit_all_sessions,
)
from examples.database import connection


def _make_session_mock() -> MagicMock:
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.in_transaction.return_value = True
    return session


async def test_callback_called_before_commit() -> None:
    session = _make_session_mock()
    order: list[str] = []
    session.commit = AsyncMock(side_effect=lambda: order.append("commit"))

    async def callback(_: AsyncSession) -> None:
        order.append("before_commit")

    token = init_db_session_ctx()
    put_db_session_to_context(connection, session)
    await commit_all_sessions(before_commit=callback)
    await reset_db_session_ctx(token, with_close=False)

    assert order == ["before_commit", "commit"]


async def test_callback_receives_session() -> None:
    session = _make_session_mock()
    received: list[object] = []

    async def callback(_session: AsyncSession) -> None:
        received.append(_session)

    token = init_db_session_ctx()
    put_db_session_to_context(connection, session)
    await commit_all_sessions(before_commit=callback)
    await reset_db_session_ctx(token, with_close=False)

    assert received == [session]


async def test_no_callback_when_none() -> None:
    session = _make_session_mock()

    token = init_db_session_ctx()
    put_db_session_to_context(connection, session)
    await commit_all_sessions(before_commit=None)
    await reset_db_session_ctx(token, with_close=False)

    session.commit.assert_awaited_once()


async def test_no_callback_when_not_in_transaction() -> None:
    session = _make_session_mock()
    session.in_transaction.return_value = False
    callback = AsyncMock()

    token = init_db_session_ctx()
    put_db_session_to_context(connection, session)
    await commit_all_sessions(before_commit=callback)
    await reset_db_session_ctx(token, with_close=False)

    callback.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_no_callback_on_error_status_code() -> None:
    session = _make_session_mock()
    callback = AsyncMock()

    token = init_db_session_ctx()
    put_db_session_to_context(connection, session)
    await auto_commit_by_status_code(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR, before_commit=callback
    )
    await reset_db_session_ctx(token, with_close=False)

    callback.assert_not_awaited()
    session.rollback.assert_awaited_once()


async def test_callback_called_on_success_status_code() -> None:
    session = _make_session_mock()
    callback = AsyncMock()

    token = init_db_session_ctx()
    put_db_session_to_context(connection, session)
    await auto_commit_by_status_code(
        status_code=HTTPStatus.OK, before_commit=callback
    )
    await reset_db_session_ctx(token, with_close=False)

    callback.assert_awaited_once_with(session)
    session.commit.assert_awaited_once()


async def test_callback_exception_prevents_commit() -> None:
    session = _make_session_mock()

    async def failing_callback(_: AsyncSession) -> None:
        raise ValueError("validation failed")

    token = init_db_session_ctx()
    put_db_session_to_context(connection, session)

    with pytest.raises(ValueError, match="validation failed"):
        await commit_all_sessions(before_commit=failing_callback)

    await reset_db_session_ctx(token, with_close=False)

    session.commit.assert_not_awaited()
