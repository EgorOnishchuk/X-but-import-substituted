"""
Модели уровня приложения.
"""

import uuid
from typing import Any

from sqlalchemy import Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DataModel:
    """
    Модель, хранящая данные. Это может быть ORM модель или сущность, представляющее другое хранилище (ФС и т.д.).
    """

    readable_name: str

    id: Any


class SQLAlchemyModel(AsyncAttrs, DeclarativeBase, DataModel):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
