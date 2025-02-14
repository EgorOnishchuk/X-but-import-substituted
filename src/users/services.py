from hashlib import sha256
from uuid import UUID

from src.errors import SelfActionError
from src.users.repositories import UserRepository
from src.users.schemas import (
    PydanticUserDetailed,
    PydanticUserNotDetailed,
    PydanticUserPersonal,
    PydanticUserSafe,
)


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository: UserRepository = repository

    async def authenticate(self, key: UUID) -> PydanticUserDetailed:
        return await self._repository.get_by_key(self._encode(key))

    async def find_by_id(self, id_: UUID) -> PydanticUserDetailed:
        return await self._repository.get_by_id(id_)

    async def sign_up(self, user: PydanticUserPersonal) -> PydanticUserNotDetailed:
        return await self._repository.create(
            PydanticUserSafe(name=user.name, key=self._encode(user.key))
        )

    async def follow(self, following_id: UUID, follower_id: UUID) -> None:
        self._check_not_owned(following_id, follower_id)

        await self._repository.create_follow(following_id, follower_id)

    async def unfollow(self, following_id: UUID, follower_id: UUID) -> None:
        """
        Удаляет отношение «следование» (отписка) между пользователями.
        :param following_id: ID пользователя, отмеченного как отслеживаемого.
        :param follower: Тот, кто отслеживает.
        """
        await self._repository.delete_follow(following_id, follower_id)

    @staticmethod
    def _encode(key: UUID) -> str:
        return sha256(str(key).encode()).hexdigest()

    @staticmethod
    def _check_not_owned(following_id: UUID, follower_id: UUID) -> None:
        if following_id == follower_id:
            raise SelfActionError("Unable to follow yourself.")
