# Testing

The library provides several ready-made utils that can be used in tests,
for example in fixtures. It helps write tests that share a common transaction
between the test and the application, so data isolation between tests is
achieved through fast transaction rollback.


You can see the capabilities in the examples:

[Here are tests with a common transaction between the
application and the tests.](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/examples/fastapi_example/tests/transactional/__init__.py)


[And here's an example with different transactions.](https://github.com/krylosov-aa/context-async-sqlalchemy/blob/main/examples/fastapi_example/tests/non_transactional/__init__.py)
