from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from src.repositories import SQLAlchemyRepository
from src.schemas import dto_from_obj, obj_from_dto
from src.users.errors import UnauthenticatedError
from src.users.models import SQLAlchemyUser
from src.users.schemas import (
    PydanticUserDetailed,
    PydanticUserNotDetailed,
    PydanticUserSafe,
    UserDetailed,
    UserNotDetailed,
)


class UserRepository(ABC):
    @dto_from_obj(UserDetailed)
    @abstractmethod
    async def get_by_key(self, key: str) -> Any:
        pass

    @dto_from_obj(UserDetailed)
    @abstractmethod
    async def get_by_id(self, id_: UUID) -> Any:
        pass

    @dto_from_obj(UserNotDetailed)
    @abstractmethod
    async def create(self, user: PydanticUserSafe) -> Any:
        pass

    @abstractmethod
    async def create_follow(self, following_id: UUID, follower_id: UUID) -> None:
        pass

    @abstractmethod
    async def delete_follow(self, following_id: UUID, follower_id: UUID) -> None:
        pass


class SQLAlchemyUserRepository(SQLAlchemyRepository, UserRepository):
    @dto_from_obj(PydanticUserDetailed)
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

    @dto_from_obj(PydanticUserDetailed)
    async def get_by_id(self, id_: UUID) -> SQLAlchemyUser:
        return await self._get_by_id(
            id_, SQLAlchemyUser, (SQLAlchemyUser.following, SQLAlchemyUser.followers)
        )

    @dto_from_obj(PydanticUserNotDetailed)
    @obj_from_dto(SQLAlchemyUser)
    async def create(self, user: PydanticUserSafe) -> SQLAlchemyUser:
        return await self._create(user)

    async def create_follow(self, following_id: UUID, follower_id: UUID) -> None:
        following = await self._get_by_id(
            following_id,
            SQLAlchemyUser,
            (SQLAlchemyUser.following, SQLAlchemyUser.followers),
        )

        await self._append_related_by_id(
            following.followers,
            follower_id,
            SQLAlchemyUser,
            (SQLAlchemyUser.following, SQLAlchemyUser.followers),
        )

    async def delete_follow(self, following_id: UUID, follower_id: UUID) -> None:
        following = await self._get_by_id(
            following_id,
            SQLAlchemyUser,
            (SQLAlchemyUser.following, SQLAlchemyUser.followers),
        )

        await self._remove_related_by_id(
            following.followers,
            follower_id,
            SQLAlchemyUser,
            (SQLAlchemyUser.following, SQLAlchemyUser.followers),
        )
