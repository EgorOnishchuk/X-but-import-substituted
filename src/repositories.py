"""
Типовые операции, независимые от типа хранимых данных (преимущественно CRUD).
"""

from collections.abc import Sequence
from contextlib import suppress
from typing import Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from src.errors import AlreadyExistsError, NotFoundError
from src.models import SQLAlchemyIDModel


class SQLAlchemyRepository:
    T = TypeVar("T", bound=SQLAlchemyIDModel)

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def _get_by_id(
        self,
        id_: UUID,
        model: Type[T],
        relationships: tuple[
            InstrumentedAttribute[SQLAlchemyIDModel]
            | InstrumentedAttribute[list[SQLAlchemyIDModel]],
            ...,
        ],
    ) -> T:
        try:
            return (
                await self._session.execute(
                    select(model)
                    .where(model.id == id_)
                    .options(*[selectinload(rel) for rel in relationships])
                )
            ).scalar_one()
        except NoResultFound:
            raise NotFoundError(f"Requested {model.__readable_name__} not found")

    async def _get_all(
        self,
        model: Type[T],
        relationships: tuple[
            InstrumentedAttribute[SQLAlchemyIDModel]
            | InstrumentedAttribute[list[SQLAlchemyIDModel]],
            ...,
        ],
    ) -> Sequence[T]:
        return (
            (
                await self._session.execute(
                    select(model).options(*[selectinload(rel) for rel in relationships])
                )
            )
            .scalars()
            .all()
        )

    async def _create(self, record: T) -> T:
        try:
            self._session.add(record)
            await self._session.flush()
        except IntegrityError:
            raise AlreadyExistsError(
                f"{record.__readable_name__.capitalize()} already exists."
            )

        return record

    async def _delete_by_id(
        self,
        id_: UUID,
        model: Type[SQLAlchemyIDModel],
        relationships: tuple[
            InstrumentedAttribute[SQLAlchemyIDModel]
            | InstrumentedAttribute[list[SQLAlchemyIDModel]],
            ...,
        ],
    ) -> None:
        """
        Попытка удалить несуществующую запись не вызывает ошибок, т.к. результат в любом случае соответствует
        ожидаемому — запись отсутствует.
        """
        record = await self._get_by_id(id_, model, relationships)

        await self._session.delete(record)

    async def _append_related_by_id(
        self,
        list_: list[T],
        related_id: UUID,
        related_model: Type[T],
        related_relationships: tuple[
            InstrumentedAttribute[SQLAlchemyIDModel]
            | InstrumentedAttribute[list[SQLAlchemyIDModel]],
            ...,
        ],
    ) -> None:
        """
        Попытка создать уже существующее отношение не вызывает ошибок, т.к. результат в любом случае соответствует
        ожидаемому — отношение присутствует.
        """
        related = await self._get_by_id(
            related_id, related_model, related_relationships
        )

        list_.append(related)

    async def _remove_related_by_id(
        self,
        list_: list[T],
        related_id: UUID,
        related_model: Type[T],
        related_relationships: tuple[
            InstrumentedAttribute[SQLAlchemyIDModel]
            | InstrumentedAttribute[list[SQLAlchemyIDModel]],
            ...,
        ],
    ) -> None:
        """
        Попытка удалить несуществующее отношение не вызывает ошибок, т.к. результат в любом случае соответствует
        ожидаемому — отношение отсутствует.
        """
        related = await self._get_by_id(
            related_id, related_model, related_relationships
        )

        with suppress(ValueError):
            list_.remove(related)
