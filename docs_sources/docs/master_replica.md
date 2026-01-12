# Using multiple database hosts (master/replica)

`db_session` and other functions accept a `DBConnect` instance as
input.
This approach allows you to work with multiple hosts simultaneously.
This system allows you to manage scalability and reliability.

- **Master** (also called **Primary**): The main database host that handles all write operations (INSERT, UPDATE, DELETE) and read operations. It is the single source of truth
- **Replica** (also called **Standby** or **Secondary**): Secondary database host(s) which run READ-ONLY versions of your information and receive updates from the master database.

`DBConnect` accepts factory functions instead of ready-made objects, making it easy to switch hosts when needed.

`libpq` can detect the master and replica when creating an engine,
but it only does this once - at creation time.
The `before_create_session_handler` hook allows you to change the host at
runtime if the master or replica changes.
You need third-party functionality to determine which host is the master or the replica.

#### I have an extremely lightweight microservice [pg-status](https://github.com/krylosov-aa/pg-status) that fits perfectly here.

The engine is not created when `DBConnect` initializes, also known as lazy initialization.
It is created only on the first request.
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
