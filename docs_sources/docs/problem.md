# The Problem It Solves

SQLAlchemy uses an engine that manages the connection pool.
The engine must remain active for as long as the application is
running, so it can quickly provide ready-to-use connections whenever the
application needs them.

In the application, we work with sessions.
A session obtains a single connection from the pool and should have a short
lifespan - usually lasting only for the duration of a single request, or even
less.

![Engine_and_session.png](img/engine_session_schema.png)

Let's see what existing solutions are available to manage sessions:

### Manual solution

This is how the code ends up being duplicated,
and two connections and two transactions are used - even though
in many cases only one connection and one transaction are actually needed.

```python
@app.post("/users/")
async def create_user(name):
    await insert_user(name)
    await insert_user_profile(name)


async def insert_user(name):
    async with get_async_session() as session:
        async with session.begin():
            await session.execute(stmt)


async def insert_user_profile(name):
    async with get_async_session() as session:
        async with session.begin():
            await session.execute(stmt)
```

You can move the duplicated code to a higher level, which will result in using
a single connection and a single transaction.


```python
@app.post("/users/")
async def create_user(name:):
    async with get_async_session() as session:
        async with session.begin():
            await insert_user(name, session)
            await insert_user_profile(name, session)


async def insert_user(name, session):
    await session.execute(stmt)


async def insert_user_profile(name, session):
    await session.execute(stmt)
```

But if you look at it more broadly, the code duplication doesn’t actually go
away - you still have to do this in every handler.


```python
@app.post("/dogs/")
async def create_dog(name):
    async with get_async_session() as session:
        async with session.begin():
            ...


@app.post("/cats")
async def create_cat(name):
    async with get_async_session() as session:
        async with session.begin():
            ...
```

You also have to set everything up yourself.
No ready-made integration solutions are used - which means freedom on one
hand, but a lot of code on the other.

### Dependency

You can use a dependency. For example, in FastAPI, it looks like this:

```python
async def get_atomic_session():
    async with session_maker() as session:
        async with session.begin():
            yield session


@app.post("/dogs/")
async def create_dog(name, session=Depends(get_atomic_session)):
    ...


@app.post("/cats/")
async def create_cat(name, session=Depends(get_atomic_session)):
    ...
```

There are two problems here:

1. You can’t close the session or transaction prematurely, because the
dependency is responsible for that.
2. The session has to be passed all the way down the stack to the place where
it’s actually needed.


By the way, there’s no ready-made solution for integrating with the framework
- you have to implement the dependency yourself.

### Wrappers over sqlalachemy

There are various wrappers that often provide more convenient integration.

Litestar, for example, has the same advantages and disadvantages as using
dependencies:

```python
config = SQLAlchemyAsyncConfig(
    connection_string=URL
)

sqlalchemy_plugin = SQLAlchemyInitPlugin(config)


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User


@post("/users")
async def create_user(data: User, repo: UserRepository):
    await repo.add(data)  # <- insert into User
```

Here’s an example using Ormar:

```python
class BaseMeta(ormar.ModelMeta):
    ...


class User(ormar.Model):
    ...


@app.post("/users/")
async def create_user(name):
    await User.objects.create(name=name)
```

The main problem with wrappers is that they require developers to learn
something new.
They introduce their own syntax - so even if a developer is familiar with
SQLAlchemy, it doesn’t mean they’ll understand the wrapper.

Wrappers are also often designed for convenience when working with simple
CRUD operations, but writing complex SQL queries with them can be very
challenging.


### Solution

And this library solves all of these issues:

- Easy integration with web frameworks
- Automatic management of engine, session, and transaction lifecycles
- Ability to manually close a session at any time, without waiting for the
end of process
- Access to a session from the context only where it’s actually needed
