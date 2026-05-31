from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from context_async_sqlalchemy.connect import DBConnect


def _make_engine() -> MagicMock:
    engine = MagicMock()
    engine.dispose = AsyncMock()
    return engine


def _make_connection(
    host: str | None = "some_host",
    handler: AsyncMock | None = None,
) -> tuple[DBConnect, MagicMock, MagicMock]:
    engine_creator = MagicMock(side_effect=lambda host: _make_engine())
    session_maker_creator = MagicMock(side_effect=lambda engine: MagicMock())
    conn = DBConnect(
        engine_creator=engine_creator,
        session_maker_creator=session_maker_creator,
        host=host,
        before_create_session_handler=handler,
    )
    return conn, engine_creator, session_maker_creator


async def test_connect_empty_host_raises() -> None:
    conn, _, _ = _make_connection()
    with pytest.raises(ValueError, match="host must not be empty"):
        await conn.connect("")


async def test_change_host_empty_host_raises() -> None:
    conn, _, _ = _make_connection()
    with pytest.raises(ValueError, match="host must not be empty"):
        await conn.change_host("")


async def test_session_maker_without_host_raises() -> None:
    conn, _, _ = _make_connection(host=None)
    with pytest.raises(ValueError, match="host is not set"):
        await conn.session_maker()


async def test_session_maker_initializes_lazily() -> None:
    conn, engine_creator, session_maker_creator = _make_connection()
    assert conn._engine is None
    assert conn._session_maker is None

    await conn.session_maker()

    engine_creator.assert_called_once_with("some_host")
    session_maker_creator.assert_called_once()
    assert conn._engine is not None
    assert conn._session_maker is not None


async def test_session_maker_reuses_existing_connection() -> None:
    conn, engine_creator, _ = _make_connection()
    await conn.session_maker()
    await conn.session_maker()

    assert engine_creator.call_count == 1


async def test_change_host_same_host_does_not_reconnect() -> None:
    conn, engine_creator, _ = _make_connection(host="host1")
    await conn.session_maker()
    calls_before = engine_creator.call_count

    await conn.change_host("host1")

    assert engine_creator.call_count == calls_before


async def test_change_host_different_host_reconnects() -> None:
    conn, engine_creator, _ = _make_connection(host="host1")
    await conn.session_maker()
    old_engine = conn._engine

    await conn.change_host("host2")

    assert conn.host == "host2"
    assert conn._engine is not old_engine
    assert engine_creator.call_count == 2
    engine_creator.assert_called_with("host2")


async def test_close_resets_engine_and_session_maker() -> None:
    conn, _, _ = _make_connection()
    await conn.session_maker()
    assert conn._engine is not None
    assert conn._session_maker is not None

    await conn.close()

    assert conn._engine is None
    assert conn._session_maker is None


async def test_close_disposes_engine() -> None:
    conn, _, _ = _make_connection()
    await conn.session_maker()
    engine = conn._engine
    assert engine is not None
    dispose_mock = cast("AsyncMock", engine.dispose)

    await conn.close()

    dispose_mock.assert_awaited_once()


async def test_before_create_session_handler_is_called() -> None:
    handler = AsyncMock()
    conn, _, _ = _make_connection(handler=handler)

    await conn.session_maker()

    handler.assert_awaited_once_with(conn)


async def test_before_create_session_handler_repeats() -> None:
    handler = AsyncMock()
    conn, _, _ = _make_connection(handler=handler)

    await conn.session_maker()
    await conn.session_maker()

    assert handler.await_count == 2
