"""
An example of fast-running tests, as the transaction for both the test and
    the application is shared.
This allows data isolation to be achieved by rolling back the transaction
    rather than deleting data from tables.

It's not exactly fair testing, because the app doesn't manage the session
    itself.
But for most basic tests, it's sufficient.
On the plus side, these tests run faster.
"""

from http import HTTPStatus

import pytest
from httpx import AsyncClient
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
