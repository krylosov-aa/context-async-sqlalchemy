"""
An example of integration tests.
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
"""
