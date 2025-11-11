import asyncio
from typing import Any, Callable, Coroutine

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)

EngineCreatorFunc = Callable[[str], AsyncEngine]
SessionMakerCreatorFunc = Callable[
    [AsyncEngine], async_sessionmaker[AsyncSession]
]
AsyncFunc = Callable[["DBConnect"], Coroutine[Any, Any, None]]


class DBConnect:
    """stores the database connection parameters"""

    def __init__(self) -> None:
        self.host: str | None = None
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None

        self.engine_creator: EngineCreatorFunc | None = None
        self.session_maker_creator: SessionMakerCreatorFunc | None = None
        self.before_create_session_handler: AsyncFunc | None = None
        self._lock = asyncio.Lock()

    async def connect(self, host: str) -> None:
        """initiates engine and session maker"""
        assert host
        async with self._lock:
            await self._connect(host)

    async def change_host(self, host: str) -> None:
        """Renews the connection if a host needs to be changed"""
        assert host
        async with self._lock:
            if host != self.host:
                await self._connect(host)

    async def create_session(self) -> AsyncSession:
        """Creates a new session"""
        if self.before_create_session_handler:
            await self.before_create_session_handler(self)
        maker = await self.get_session_maker()
        return maker()

    async def get_session_maker(self) -> async_sessionmaker[AsyncSession]:
        """Gets the session maker"""
        if not self._session_maker:
            assert self.host
            await self.connect(self.host)

        assert self._session_maker
        return self._session_maker

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
        self._engine = None

    async def _connect(self, host: str) -> None:
        self.host = host
        await self.close()
        assert self.engine_creator
        self._engine = self.engine_creator(host)
        assert self.session_maker_creator
        self._session_maker = self.session_maker_creator(self._engine)


master_connect = DBConnect()
replica_connect = DBConnect()
