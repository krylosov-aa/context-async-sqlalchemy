"""
With set_test_context you can call funcs straight
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from context_async_sqlalchemy.test_utils import set_test_context

from examples.fastapi_example.routes.atomic import atomic_base_example
from ..conftest import count_rows_example_table


@pytest.mark.asyncio
async def test_atomic_base_example(
    db_session_test: AsyncSession,
) -> None:
    async with set_test_context(auto_close=True):
        await atomic_base_example()

    assert await count_rows_example_table(db_session_test) == 2
