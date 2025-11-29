"""
Fair tests in which the application manages the session lifecycle itself.
Data isolation between tests is performed by running trunks before and after
    each test.
This is fair testing, but slower.
"""

import pytest
from http import HTTPStatus

from httpx import AsyncClient
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from ..conftest import count_rows_example_table


@pytest.mark.asyncio
async def test_atomic_base_example(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    response = await client.post("/atomic_base_example")

    assert response.status_code == HTTPStatus.OK
    assert await count_rows_example_table(db_session_test) == 2


@pytest.mark.asyncio
async def test_simple_usage(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    response = await client.post("/simple_usage")

    assert response.status_code == HTTPStatus.OK
    assert await count_rows_example_table(db_session_test) == 1


@pytest.mark.asyncio
async def test_atomic_and_previous_transaction(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    try:
        await client.post(
            "/atomic_and_previous_transaction",
        )
    except InvalidRequestError:
        ...
    else:
        raise Exception()

    assert await count_rows_example_table(db_session_test) == 5


@pytest.mark.asyncio
async def test_early_commit(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    response = await client.post("/early_commit")

    assert response.status_code == HTTPStatus.OK
    assert await count_rows_example_table(db_session_test) == 4


@pytest.mark.asyncio
async def test_concurrent_queries(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    response = await client.post("/concurrent_queries")

    assert response.status_code == HTTPStatus.OK
    assert await count_rows_example_table(db_session_test) == 5


@pytest.mark.asyncio
async def test_early_rollback(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    response = await client.post("/early_rollback")

    assert response.status_code == HTTPStatus.OK
    assert await count_rows_example_table(db_session_test) == 0


@pytest.mark.asyncio
async def test_auto_rollback_by_exception(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    try:
        await client.post(
            "/auto_rollback_by_exception",
        )
    except Exception:
        ...
    else:
        raise Exception("an exception was expected")

    assert await count_rows_example_table(db_session_test) == 0


@pytest.mark.asyncio
async def test_auto_rollback_by_status_code(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    response = await client.post("/auto_rollback_by_status_code")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert await count_rows_example_table(db_session_test) == 0


@pytest.mark.asyncio
async def test_early_connection_close(
    client: AsyncClient,
    db_session_test: AsyncSession,
) -> None:
    response = await client.post("/early_connection_close")

    assert response.status_code == HTTPStatus.OK
    assert await count_rows_example_table(db_session_test) == 2
