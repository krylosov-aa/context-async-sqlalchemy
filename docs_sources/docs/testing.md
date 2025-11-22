# Testing


For testing with a real database, there is one important problem that needs to
be solved - data isolation between tests.

There are basically two approaches:

1. The test has its own session with which it can prepare data for the
test and verify the result of the test execution at the end.
The application has its own session. Data isolation is achieved by clearing
data from all tables at the end of each test
(as well as once before running all tests)
2. The test and the application share the same session and the same
transaction. Data isolation is achieved by rolling back the transaction
at the end of the test.

Personally, I really like the first option. Because this is an honest testing of the application.
We check how it works correctly with sessions and transactions on our own.
It is also very convenient to check the status of the database when the
test is suspended.

And sometimes there are such complex session management scenarios
(for example, concurrent query execution) in which other types of
testing are either impossible or very difficult.

The only disadvantage of such tests is the speed of their execution.
Due to the fact that we clear all the tables after each test, we spend
a lot of time on this.

This is where the second type of testing comes on the scene,
which has the only advantage in the speed of execution due to the fact
that it is very fast to roll back the transaction.


I use both approaches simultaneously in my projects.
Most of the tests where the usual and simple logic is tested,
I use a common transaction for the test and for the application. 
And where there is complex logic or it is simply not possible to
test like this, I use tests with different transactions.
This allows you to achieve good speed and good test convenience.

The library provides several utils that can be used in tests,
for example in fixtures. It helps write tests that share a common transaction
between the test and the application, so data isolation between tests is
achieved through fast transaction rollback.


You can see the capabilities in the examples:

[Here are tests with a common transaction between the
application and the tests.](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/examples/fastapi_example/tests/transactional/__init__.py)


[And here's an example with different transactions.](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/examples/fastapi_example/tests/non_transactional/__init__.py)


## Create session with autorollback

`rollback_session` creates a session that always rolls back automatically.

```python
from context_async_sqlalchemy.test_utils import rollback_session

@pytest_asyncio.fixture
async def db_session_test() -> AsyncGenerator[AsyncSession]:
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
) -> AsyncGenerator[None]:
    """
    The key thing about these tests is that we override the context in advance.
    The middleware has a special check that won't initialize the context
        if it already exists.
    """
    async with set_test_context():
        async with put_savepoint_session_in_ctx(connection, db_session_test):
            yield
```
