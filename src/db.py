"""
Управление жизненным циклом подключений к БД.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.settings import db_settings


class DBManager(ABC):
    """
    Менеджер сессий и базовой конфигурации БД.
    """

    @abstractmethod
    @asynccontextmanager
    def get_session(self) -> AsyncGenerator[Any, None]:
        """
        Получает сессию, готовую к работе.
        :return: Сессия, использование которой в контекстном менеджере автоматизирует коммит, откат и её закрытие.
        """

    @abstractmethod
    async def setup(self) -> None:
        """
        Создаёт таблицы и, при необходимости, совершает другие подготовительные действия (заполнение данными и т.д.).
        """

    @abstractmethod
    async def clear(self) -> None:
        """
        Очищает таблицы, и при необходимости, совершает другие действия по финализации.
        """


class SQLAlchemyDBManager(DBManager):
    def __init__(self, metadata: MetaData) -> None:
        self._metadata: MetaData = metadata

        self._engine: AsyncEngine = create_async_engine(
            db_settings.url,
            pool_size=db_settings.pool_size,
            max_overflow=db_settings.max_overflow,
            pool_pre_ping=db_settings.is_pool_pre_ping,
        )
        self._session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self._engine, expire_on_commit=False
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        session = self._session_maker()
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise exc
        finally:
            await session.close()

    async def setup(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(self._metadata.create_all)

    async def clear(self) -> None:
        async with self._engine.begin() as conn:
            for table in self._metadata.sorted_tables:
                await conn.execute(table.delete())
