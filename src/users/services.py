"""
Слой логики операций с пользователями.
"""

from abc import abstractmethod
from hashlib import sha256
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from src.errors import SelfActionError
from src.services import DBRepository, SQLAlchemyRepository
from src.users.errors import UnauthenticatedError
from src.users.models import DataUser, SQLAlchemyUser
from src.users.schemas import UserPersonal, UserSafe


class UserRepository(DBRepository):
    @abstractmethod
    async def get_by_key(self, key: str) -> DataUser:
        """
        Получает пользователя по ключу API.
        :param key: Зашифрованный действительный ключ API.
        :return: Пользователь.
        """

    @abstractmethod
    async def get_by_id(self, id_: UUID) -> DataUser:
        """
        Получает пользователя по ID.
        :param id_: Уникальный идентификатор.
        :return: Пользователь.
        """

    @abstractmethod
    async def create(self, user: UserSafe) -> DataUser:
        """
        Создаёт пользователя.
        :param user: Пользователь, пригодный для хранения в БД с точки зрения безопасности.
        """

    @abstractmethod
    async def create_follow(self, following: DataUser, follower: DataUser) -> None:
        """
        Создаёт отношение «следование» (подписка) между пользователями.
        :param following: Тот, кто отмечен как отслеживаемый.
        :param follower: Тот, кто отслеживает.
        """

    @abstractmethod
    async def delete_follow(self, following: DataUser, follower: DataUser) -> None:
        """
        Удаляет отношение «следование» (отписка) между пользователями.
        :param following: Тот, кто отмечен как отслеживаемый.
        :param follower: Тот, кто отслеживает.
        """


class SQLAlchemyUserRepository(SQLAlchemyRepository, UserRepository):
    async def get_by_key(self, key: str) -> SQLAlchemyUser:
        try:
            return (
                await self._session.execute(
                    select(SQLAlchemyUser)
                    .where(SQLAlchemyUser.key == key)
                    .options(
                        selectinload(SQLAlchemyUser.following),
                        selectinload(SQLAlchemyUser.followers),
                    )
                )
            ).scalar_one()
        except NoResultFound:
            raise UnauthenticatedError("Invalid credentials.")

    async def get_by_id(self, id_: UUID) -> SQLAlchemyUser:
        return await self._get_by_id(
            SQLAlchemyUser, id_, (SQLAlchemyUser.following, SQLAlchemyUser.followers)
        )

    async def create(self, user: UserSafe) -> SQLAlchemyUser:
        return await self._create(user.model_dump(), SQLAlchemyUser)

    async def create_follow(
        self, following: SQLAlchemyUser, follower: SQLAlchemyUser
    ) -> None:
        await self._append_related(following.followers, follower)

    async def delete_follow(
        self, following: SQLAlchemyUser, follower: SQLAlchemyUser
    ) -> None:
        await self._remove_related(following.followers, follower)


class UserService:
    """
    Сервис для работы с пользователями.
    """

    def __init__(self, repository: UserRepository) -> None:
        self._repository: UserRepository = repository

    async def get_by_key(self, key: UUID) -> DataUser:
        """
        Получает пользователя по ключу API.
        :param key: Незашифрованный действительный ключ API.
        :return: Пользователь.
        """
        return await self._repository.get_by_key(self._encode(key))

    async def get_by_id(self, id_: UUID) -> DataUser:
        """
        Получает пользователя по ID.
        :param id_: Уникальный идентификатор.
        :return: Пользователь.
        """
        return await self._repository.get_by_id(id_)

    async def create(self, user: UserPersonal) -> DataUser:
        """
        Создаёт пользователя.
        :param user: Данные регистрации, полученные от пользователя.
        :return: Зарегистрированный пользователь.
        """
        return await self._repository.create(
            UserSafe(name=user.name, key=self._encode(user.key))
        )

    async def create_follow(self, following_id: UUID, follower: DataUser) -> None:
        """
        Создаёт отношение «следование» (подписка) между пользователями.
        :param following_id: ID пользователя, отмеченного как отслеживаемого.
        :param follower: Тот, кто отслеживает.
        """
        self._check_not_owned(following_id, follower.id)
        following = await self._repository.get_by_id(following_id)

        await self._repository.create_follow(following, follower)

    async def delete_follow(self, following_id: UUID, follower: DataUser) -> None:
        """
        Удаляет отношение «следование» (отписка) между пользователями.
        :param following_id: ID пользователя, отмеченного как отслеживаемого.
        :param follower: Тот, кто отслеживает.
        """
        following = await self._repository.get_by_id(following_id)
        await self._repository.delete_follow(following, follower)

    @staticmethod
    def _encode(key: UUID) -> str:
        return sha256(str(key).encode()).hexdigest()

    @staticmethod
    def _check_not_owned(following_id: UUID, follower_id: UUID) -> None:
        if following_id == follower_id:
            raise SelfActionError("Unable to follow yourself.")
