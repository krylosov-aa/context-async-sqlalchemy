from unittest.mock import AsyncMock, MagicMock

import pytest

from context_async_sqlalchemy import (
    init_db_session_ctx,
    is_context_initiated,
    put_db_session_to_context,
    reset_db_session_ctx,
    run_in_new_ctx,
)
from examples.database import connection


def _make_session_mock() -> MagicMock:
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.in_transaction.return_value = True
    return session


async def test_run_in_new_ctx_returns_result() -> None:
    async def func() -> int:
        return 1

    assert await run_in_new_ctx(func) == 1


async def test_run_in_new_ctx_passes_args() -> None:
    async def add(first: int, second: int) -> int:
        return first + second

    assert await run_in_new_ctx(add, 3, second=4) == 7


async def test_run_in_new_ctx_reraises_exception() -> None:
    async def raises() -> None:
        raise ValueError("inner error")

    with pytest.raises(ValueError, match="inner error"):
        await run_in_new_ctx(raises)


async def test_run_in_new_ctx_without_outer_ctx() -> None:
    assert is_context_initiated() is False

    async def work() -> int:
        return 1

    assert await run_in_new_ctx(work) == 1
    assert is_context_initiated() is False


async def test_run_in_new_ctx_isolated_context() -> None:
    outer_token = init_db_session_ctx()
    seen: list[bool] = []

    async def capture() -> None:
        seen.append(is_context_initiated())

    await run_in_new_ctx(capture)

    assert seen == [True]
    assert is_context_initiated() is True
    await reset_db_session_ctx(outer_token)


async def test_run_in_new_ctx_commits_on_success() -> None:
    session_mock = _make_session_mock()

    async def put_session() -> None:
        put_db_session_to_context(connection, session_mock)

    await run_in_new_ctx(put_session)

    session_mock.commit.assert_awaited_once()


async def test_run_in_new_ctx_rollbacks_on_exception() -> None:
    session_mock = _make_session_mock()

    async def put_session_and_raise() -> None:
        put_db_session_to_context(connection, session_mock)
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        await run_in_new_ctx(put_session_and_raise)

    session_mock.rollback.assert_awaited_once()


async def test_run_in_new_ctx_outer_ctx_unaffected() -> None:
    outer_session = _make_session_mock()
    outer_token = init_db_session_ctx()
    put_db_session_to_context(connection, outer_session)

    async def inner_work() -> None:
        pass

    await run_in_new_ctx(inner_work)

    outer_session.commit.assert_not_awaited()
    outer_session.rollback.assert_not_awaited()
    await reset_db_session_ctx(outer_token, with_close=False)
