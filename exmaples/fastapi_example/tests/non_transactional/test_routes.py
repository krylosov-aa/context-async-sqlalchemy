"""
Fair tests in which the application manages the session lifecycle itself.
Data isolation between tests is performed by running trunks before and after
    each test.
This is fair testing, but slower.
"""

import pytest
from http import HTTPStatus

from httpx import AsyncClient
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from exmaples.fastapi_example.models import ExampleTable


@pytest.mark.asyncio
async def test_example_with_db_session(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    # Act
    response = await client.post(
        "/example_with_db_session",
    )

    # Assert
    assert response.status_code == HTTPStatus.OK

    result = await db_session_test.execute(select(ExampleTable))
    row = result.scalar_one()
    assert row.text == "example_with_db_session"


@pytest.mark.asyncio
async def test_example_with_db_session_and_atomic(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    """
    Since the handler involves manual session management,
        such a handler should only be tested in non-transactional tests.
    """
    # Act
    response = await client.post(
        "/example_with_db_session_and_atomic",
    )

    # Assert
    assert response.status_code == HTTPStatus.OK

    result = await db_session_test.execute(select(ExampleTable))
    row = result.scalar_one()
    assert row.text == "example_with_db_session_and_atomic"


@pytest.mark.asyncio
async def test_example_with_db_session_and_manual_close(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    """
    Since the handler involves manual session management,
        such a handler should only be tested in non-transactional tests.
    """
    # Act
    response = await client.post(
        "/example_with_db_session_and_manual_close",
    )

    # Assert
    assert response.status_code == HTTPStatus.OK

    result = await db_session_test.execute(select(ExampleTable))
    rows = result.scalars().all()
    assert len(rows) == 4
    for row in rows:
        assert row.text == "example_with_db_session_and_manual_close"


@pytest.mark.asyncio
async def test_example_multiple_sessions(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    """
    Since the handler involves manual session management,
        such a handler should only be tested in non-transactional tests.
    """
    # Act
    response = await client.post(
        "/example_multiple_sessions",
    )

    # Assert
    assert response.status_code == HTTPStatus.OK

    result = await db_session_test.execute(select(ExampleTable))
    rows = result.scalars().all()
    assert len(rows) == 5
    for row in rows:
        assert row.text == "example_multiple_sessions"


@pytest.mark.asyncio
async def test_example_with_manual_rollback(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    """
    Since the handler involves manual session management,
        such a handler should only be tested in non-transactional tests.
    """
    # Act
    response = await client.post(
        "/example_with_manual_rollback",
    )

    # Assert
    assert response.status_code == HTTPStatus.OK

    exist_row = await db_session_test.execute(
        select(exists().select_from(ExampleTable))
    )
    assert exist_row.scalar() is False


@pytest.mark.asyncio
async def test_example_with_exception(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    # Act
    try:
        await client.post(
            "/example_with_exception",
        )
    except Exception:
        ...
    else:
        raise Exception("an exception was expected")

    # Assert
    exist_row = await db_session_test.execute(
        select(exists().select_from(ExampleTable))
    )
    assert exist_row.scalar() is False


@pytest.mark.asyncio
async def test_example_with_http_exception(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    # Act
    response = await client.post(
        "/example_with_http_exception",
    )

    # Assert
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    exist_row = await db_session_test.execute(
        select(exists().select_from(ExampleTable))
    )
    assert exist_row.scalar() is False
