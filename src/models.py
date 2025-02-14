import uuid

from sqlalchemy import Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class SQLAlchemyModel(AsyncAttrs, DeclarativeBase):
    __readable_name__: str
    __abstract__ = True


class SQLAlchemyIDModel(SQLAlchemyModel):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
