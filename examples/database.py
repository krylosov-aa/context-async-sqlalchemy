"""
The module that defines the database connection parameters
"""

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from context_async_sqlalchemy import DBConnect


def create_engine(host: str) -> AsyncEngine:
    """
    database connection parameters
    """

    # In production code, you will probably take these parameters from env
    pg_user = "krylosov-aa"
    pg_password = "test"
    pg_port = 6432
    pg_db = "test"
    return create_async_engine(
        f"postgresql+asyncpg://"
        f"{pg_user}:{pg_password}"
        f"@{host}:{pg_port}"
        f"/{pg_db}",
        future=True,
        pool_pre_ping=True,
    )


def create_session_maker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """session parameters"""
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


connection = DBConnect(
    host="127.0.0.1",
    engine_creator=create_engine,
    session_maker_creator=create_session_maker,
)
