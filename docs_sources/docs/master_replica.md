# Master/Replica or several databases at the same time

This is why `db_session` and other functions accept a `DBConnect` instance as
input.
This approach allows you to work with multiple hosts simultaneously -
for example, with both a master and a replica.

`DBConnect` can also accept factory functions instead of ready-made objects,
making it easy to switch hosts when needed.

For example, `libpq` can detect the master and replica when creating an engine,
but it only does this once - at creation time.
The before_create_session_handler hook allows you to change the host at
runtime if the master or replica changes.
You’ll need third-party functionality to determine which host is the master
or the replica.


[Hopefully, I’ll be able to provide a ready-made solution for this soon.](https://github.com/krylosov-aa/context-async-sqlalchemy/issues/2).

The engine is not created immediately when `DBConnect` is initialized -
it is created only on the first request.
The library uses lazy initialization in many places.

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
