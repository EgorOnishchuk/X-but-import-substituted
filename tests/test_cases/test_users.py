from hashlib import sha256
from typing import Type
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from faker import Faker

from src.errors import AlreadyExistsError, NotFoundError, SelfActionError
from src.users.errors import UnauthenticatedError
from src.users.models import SQLAlchemyUser
from src.users.schemas import UserPersonal
from src.users.services import SQLAlchemyUserRepository, UserService
from tests.factories import SQLAlchemyUserFactory
from tests.test_cases.test_model import TestSQLAlchemyModel


class TestSQLAlchemyUsers(TestSQLAlchemyModel):
    factory_: Type[SQLAlchemyUserFactory] = SQLAlchemyUserFactory
    service: Type[UserService] = UserService
    repository: Type[SQLAlchemyUserRepository] = SQLAlchemyUserRepository

    @pytest_asyncio.fixture
    async def user(self) -> SQLAlchemyUser:
        return await self.factory_()

    @pytest.fixture
    def built_user(self) -> UserPersonal:
        faker = Faker()
        return UserPersonal(name=faker.name(), key=uuid4())

    @pytest_asyncio.fixture
    async def user_and_raw_key(self) -> tuple[SQLAlchemyUser, UUID]:
        raw_key = uuid4()
        user_ = await self.factory_(key=sha256(str(raw_key).encode()).hexdigest())

        return user_, raw_key

    @pytest_asyncio.fixture
    async def followers(self) -> tuple[SQLAlchemyUser, SQLAlchemyUser]:
        user_1, user_2 = await self.factory_.create_batch(2)
        await self.test_service.create_follow(user_1.id, user_2)

        return user_1, user_2

    @pytest.mark.asyncio
    async def test_get_by_key(
        self, user_and_raw_key: tuple[SQLAlchemyUser, UUID]
    ) -> None:
        user, raw_key = user_and_raw_key

        assert user == (await self.test_service.get_by_key(raw_key))

    @pytest.mark.asyncio
    async def test_get_by_nonexistent_key(
        self, user_and_raw_key: tuple[SQLAlchemyUser, UUID]
    ) -> None:
        user, key = user_and_raw_key

        with pytest.raises(UnauthenticatedError):
            await self.test_service.get_by_key(self.get_new_uuid(key))

    @pytest.mark.asyncio
    async def test_get_by_id(self, user: SQLAlchemyUser) -> None:
        assert user == (await self.test_service.get_by_id(user.id))

    @pytest.mark.asyncio
    async def test_get_by_nonexistent_id(self, user: SQLAlchemyUser) -> None:
        with pytest.raises(NotFoundError):
            await self.test_service.get_by_id(self.get_new_uuid(user.id))

    @pytest.mark.asyncio
    async def test_create(self, built_user: UserPersonal) -> None:
        assert built_user.name == (await self.test_service.create(built_user)).name

    @pytest.mark.asyncio
    async def test_follow(
        self, followers: tuple[SQLAlchemyUser, SQLAlchemyUser]
    ) -> None:
        user_1, user_2 = followers

        assert user_1.followers == [user_2]

    @pytest.mark.asyncio
    async def test_follow_self(self, user: SQLAlchemyUser) -> None:
        with pytest.raises(SelfActionError):
            await self.test_service.create_follow(user.id, user)

    @pytest.mark.asyncio
    async def test_unfollow(
        self, followers: tuple[SQLAlchemyUser, SQLAlchemyUser]
    ) -> None:
        user_1, user_2 = followers
        await self.test_service.delete_follow(user_1.id, user_2)

        assert user_1.followers == []

    @pytest.mark.asyncio
    async def test_unfollow_nonexistent(
        self, followers: tuple[SQLAlchemyUser, SQLAlchemyUser]
    ) -> None:
        user_1, user_2 = followers

        await self.test_service.delete_follow(user_1.id, user_2)

    @pytest.mark.asyncio
    async def test_unfollow_self(self, user: SQLAlchemyUser) -> None:
        await self.test_service.delete_follow(user.id, user)
