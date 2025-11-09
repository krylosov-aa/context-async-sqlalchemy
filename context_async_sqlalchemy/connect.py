import asyncio
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)


class DBConnect:
    """stores the database connection parameters"""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_maker: async_sessionmaker[AsyncSession] | None = None
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        if self.engine:
            await self.engine.dispose()
        self.engine = None


db_connect = DBConnect()


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Gets the session maker"""
    assert db_connect.session_maker
    return db_connect.session_maker


def create_session() -> AsyncSession:
    """Creates a new session"""
    assert db_connect.session_maker
    return db_connect.session_maker()
