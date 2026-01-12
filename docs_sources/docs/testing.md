# Testing


When testing with a real database, one important problem needs to be solved: ensuring data isolation between tests.
There are two approaches:

1. **Separate sessions**: The test uses its own session that prepares data and
   verifies results after execution. The application also has its own session.

    - It is a more "honest" way to test the application.
    - Verifies how it handles sessions and transactions automatically.
    - The ability to inspect the database state when the test is paused.
    - Complex session management scenarios make other test methods difficult or impossible (e.g., concurrent query execution).

2. **Shared session and transaction**: The test and the application share the same session and transaction.

    - Rolling back transactions is faster and takes less time than starting a new session.



In my projects, I use both approaches at the same time:

- For most tests with simple or common logic, I use a shared transaction for the test and the application
- For more complex cases, or ones that cannot be tested with separate sessions, I use separate transactions.


The library provides several utilities that can be used in tests (e.g., fixtures).
They create tests that share a common transaction between the test
and the application. You achieve data isolation by rolling back transactions.


You can see these capabilities in the examples:

[Here are tests with a common transaction between the
application and the tests.](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/examples/fastapi_example/tests/transactional)


[And here's an example with different transactions.](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/examples/fastapi_example/tests/non_transactional)


## Create session with autorollback

`rollback_session` creates a session that always rolls back automatically.

```python
from context_async_sqlalchemy.test_utils import rollback_session

@pytest_asyncio.fixture
async def db_session_test() -> AsyncGenerator[AsyncSession, None]:
    """The session that is used inside the test"""
    async with rollback_session(connection) as session:
        yield session
```

## Override context

- `set_test_context` creates a new context
- `put_savepoint_session_in_ctx` puts into context a session that uses the
same connection as `db_session_test`,  but if you commit in this session,
then the transaction will not be committed, but save point will be released

```python
from context_async_sqlalchemy.test_utils import (
    put_savepoint_session_in_ctx,
    set_test_context,
)

@pytest_asyncio.fixture(autouse=True)
async def db_session_override(
    db_session_test: AsyncSession,
) -> AsyncGenerator[None, None]:
    """
    The key thing about these tests is that we override the context in advance.
    The middleware has a special check that won't initialize the context
        if it already exists.
    """
    async with set_test_context():
        async with put_savepoint_session_in_ctx(connection, db_session_test):
            yield
```
