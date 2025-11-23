# Shared session and transaction

The test and the application share the same session and transaction.
Data isolation is achieved by rolling back the transaction at
the end of the test.

The library provides several utilities that can be used in tests - for
example, in fixtures.
They help create tests that share a common transaction between the test
and the application, so data isolation between tests is achieved through
fast transaction rollback.


Its main advantage is speed,
as rolling back a transaction is very fast.
