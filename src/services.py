"""
Слой логики уровня приложения. Представляет типовые операции, независимые от модели (преимущественно CRUD).
"""

from abc import ABC
from contextlib import suppress
from typing import Any, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from src.errors import AlreadyExistsError, NotFoundError
from src.models import SQLAlchemyModel


class DBRepository(ABC):
    """
    Выполняет операции с БД.
    """

    def __init__(self, session: Any) -> None:
        self._session: Any = session


class SQLAlchemyRepository(DBRepository):
    T = TypeVar("T", bound=SQLAlchemyModel)

    async def _get_by_id(
        self,
        model: Type[SQLAlchemyModel],
        id_: UUID,
        relationships: tuple[
            InstrumentedAttribute[SQLAlchemyModel]
            | InstrumentedAttribute[list[SQLAlchemyModel]],
            ...,
        ],
    ) -> T:
        """
        Получает запись по ID.
        :param model: Модель записи.
        :param id_: Уникальный идентификатор.
        :param relationships: Отношения между моделями, которые необходимо догрузить.
        :return: Запись.
        :raises NotFoundError: Запись не найдена.
        """
        try:
            return (
                await self._session.execute(
                    select(model)
                    .where(model.id == id_)
                    .options(*[selectinload(rel) for rel in relationships])
                )
            ).scalar_one()
        except NoResultFound:
            raise NotFoundError(f"Requested {model.readable_name} not found.")

    async def _get_all(
        self,
        model: Type[SQLAlchemyModel],
        relationships: tuple[
            InstrumentedAttribute[SQLAlchemyModel]
            | InstrumentedAttribute[list[SQLAlchemyModel]],
            ...,
        ],
    ) -> list[T]:
        """
        Получает все записи.
        :param model: Модель записи.
        :param relationships: Отношения между моделями, которые необходимо догрузить.
        :return: Список записей.
        """
        return (
            (
                await self._session.execute(
                    select(model).options(*[selectinload(rel) for rel in relationships])
                )
            )
            .scalars()
            .all()
        )

    async def _create(self, schema: dict[str, Any], model: Type[T]) -> T:
        """
        Создаёт запись.
        :param schema: Сериализованная схема записи.
        :param model: Модель записи.
        :return: Запись.
        :raises AlreadyExistsError: Запись уже существует.
        """
        db_model = model(**schema)

        try:
            self._session.add(db_model)
            await self._session.flush()
        except IntegrityError:
            raise AlreadyExistsError(
                f"{model.readable_name.capitalize()} already exists."
            )

        return db_model

    async def _delete(self, model: SQLAlchemyModel) -> None:
        """
        Удаляет запись. Не поднимает исключение, если запись не найдена.
        :param model: Модель записи.
        """
        await self._session.delete(model)

    @staticmethod
    async def _append_related(
        list_: list[SQLAlchemyModel], related: SQLAlchemyModel
    ) -> None:
        """
        Добавляет отношение между записями. Не поднимает исключение, если запись уже присутствует.
        :param list_: Список записей, состоящих в отношении.
        :param related: Запись к добавлению.
        """
        list_.append(related)

    @staticmethod
    async def _remove_related(
        list_: list[SQLAlchemyModel], related: SQLAlchemyModel
    ) -> None:
        """
        Удаляет отношение между записями. Не поднимает исключение, если запись отсутствует.
        :param list_: Список записей, состоящих в отношении.
        :param related: Запись к удалению.
        """
        with suppress(ValueError):
            list_.remove(related)
