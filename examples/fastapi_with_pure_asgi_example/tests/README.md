# An example of integration tests.
I recommend this approach because it’s independent of the application’s
    architecture and allows you to test your application in a realistic way.

When testing with a real database, one important problem needs to be
solved - ensuring data isolation between tests.

There are basically two approaches:


1. Separate sessions

The test has its own session that it uses to prepare data and verify
results after execution.
The application also has its own session.
Data isolation is achieved by clearing all tables at the end of each test
(and once before running all tests).

2. Shared session and transaction
The test and the application share the same session and transaction.
Data isolation is achieved by rolling back the transaction at
the end of the test.

Personally, I prefer the first option, because it is a more "honest" way
to test the application.
We can verify how it handles sessions and transactions on its own.
It’s also convenient to inspect the database state when a test is paused.

Sometimes, there are complex session management scenarios (for example,
concurrent query execution) where other types of testing are either
impossible or very difficult.

The main disadvantage of this approach is the slower execution speed.
Since we clear all tables after each test, this process takes additional time.

This is where the second approach comes in - its main advantage is speed,
as rolling back a transaction is very fast.

In my projects, I use both approaches at the same time:

- For most tests with simple or common logic, I use a shared transaction
for the test and the application
- For more complex cases, or ones that cannot be tested this way,
I use separate transactions.


This combination allows for both good performance and convenient testing.

The library provides several utilities that can be used in tests - for
example, in fixtures.
They help create tests that share a common transaction between the test
and the application, so data isolation between tests is achieved through
fast transaction rollback.

You can see these capabilities in the examples:

[Here are tests with a common transaction between the
application and the tests.](transactional)


[And here's an example with different transactions.](non_transactional)
