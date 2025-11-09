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

import pytest
from http import HTTPStatus

from httpx import AsyncClient
from sqlalchemy import select
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
