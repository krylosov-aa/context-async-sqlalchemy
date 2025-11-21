# Master/Replica or several databases at the same time


This is why `db_session` and other functions accept `DBConnect` as input.
This way, you can work with multiple hosts simultaneously, for example,
with the master and the replica.


`DBConnect` also accepts factories instead of ready-made objects, so that you
can easily change the host at the right time.

For example, libpq can detect the master and replica to create an engine.
However, it only does this once during creation. `before_create_session_handler`
helps change the host in the runtime if the master or replica changes.
You need a third-party functionality that helps determine the master or
replica.
[I hope I can give you a ready solution soon too](https://github.com/krylosov-aa/context-async-sqlalchemy/issues/2).

The engine will not be created immediately when `DBConnect` is initialized.
This will only happen on the first request. The library is lazy in many places.

```python
from context_async_sqlalchemy import DBConnect

from master_replica_helper import get_master, get_replica


async def renew_master_connect(connect: DBConnect) -> None:
    """Updates the host if the master has changed"""
    master_host = await get_master()
    if master_host != connect.host:
        await connect.change_host(master_host)

        
master = DBConnect(
    ...,
    before_create_session_handler=renew_master_connect,
)


async def renew_replica_connect(connect: DBConnect) -> None:
    """Updates the host if the replica has changed"""
    replica_host = await get_replica()
    if replica_host != connect.host:
        await connect.change_host(replica_host)

        
replica = DBConnect(
    ...,
    before_create_session_handler=renew_replica_connect,
)
```
