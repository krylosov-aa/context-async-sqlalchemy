# Separate sessions

The test has its own session that it uses to prepare data and verify
results after execution.
The application also has its own session.
Data isolation is achieved by clearing all tables at the end of each test
(and once before running all tests).


We can verify how it handles sessions and transactions on its own.
It’s also convenient to inspect the database state when a test is paused.

Sometimes, there are complex session management scenarios (for example,
concurrent query execution) where other types of testing are either
impossible or very difficult.

The main disadvantage of this approach is the slower execution speed.
Since we clear all tables after each test, this process takes additional time.
