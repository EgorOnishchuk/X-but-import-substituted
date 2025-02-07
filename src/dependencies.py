"""
Зависимости приложения и другая функциональность, близкая к ним по значению (lifespan и т.д.).
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI

from src.db import DBManager, SQLAlchemyDBManager
from src.models import SQLAlchemyModel


def get_db_manager() -> DBManager:
    """
    Зависимость менеджера БД.
    :return: Менеджер БД.
    """
    return SQLAlchemyDBManager(SQLAlchemyModel.metadata)


DB_Manager = Annotated[DBManager, Depends(get_db_manager)]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Подготавливает БД перед запуском приложения. Предназначена для развёртывания, поэтому не удаляет таблицы.
    :param app: Приложение.
    """
    await get_db_manager().setup()

    yield


async def _get_session(db_manager: DB_Manager) -> AsyncGenerator[Any, None]:
    async with db_manager.get_session() as session:
        yield session


Session: Any = Annotated[Any, Depends(_get_session)]
