import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from context_async_sqlalchemy import (
    get_db_session_from_context,
    init_db_session_ctx,
    is_context_initiated,
    pop_db_session_from_context,
    put_db_session_to_context,
    reset_db_session_ctx,
)
from examples.database import connection


@pytest.mark.asyncio
async def test_init_db_session_ctx() -> None:
    assert is_context_initiated() is False

    token = init_db_session_ctx()

    assert is_context_initiated() is True

    try:
        init_db_session_ctx()
    except Exception:
        ...
    else:
        raise Exception()

    assert is_context_initiated() is True

    await reset_db_session_ctx(token)

    assert is_context_initiated() is False


@pytest.mark.asyncio
async def test_init_db_session_ctx_force(
    db_session_test: AsyncSession,
) -> None:
    token1 = init_db_session_ctx()
    put_db_session_to_context(connection, db_session_test)
    assert get_db_session_from_context(connection) is db_session_test

    token2 = init_db_session_ctx(force=True)
    assert get_db_session_from_context(connection) is None

    await reset_db_session_ctx(token2, with_close=False)
    await reset_db_session_ctx(token1, with_close=False)


@pytest.mark.asyncio
async def test_pop_db_session_from_context(
    db_session_test: AsyncSession,
) -> None:
    token = init_db_session_ctx()
    assert pop_db_session_from_context(connection) is None

    put_db_session_to_context(connection, db_session_test)
    assert pop_db_session_from_context(connection) is db_session_test
    assert pop_db_session_from_context(connection) is None

    await reset_db_session_ctx(token)


@pytest.mark.asyncio
async def test_get_db_session_from_context(
    db_session_test: AsyncSession,
) -> None:
    try:
        get_db_session_from_context(connection)
    except Exception:
        ...
    else:
        raise Exception()

    token = init_db_session_ctx()
    assert get_db_session_from_context(connection) is None

    put_db_session_to_context(connection, db_session_test)
    assert get_db_session_from_context(connection) is db_session_test
    assert get_db_session_from_context(connection) is db_session_test

    await reset_db_session_ctx(token, with_close=False)
