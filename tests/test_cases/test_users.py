from hashlib import sha256
from typing import Type
from uuid import UUID

import pytest
import pytest_asyncio

from src.errors import NotFoundError, SelfActionError
from src.settings import EXAMPLES
from src.users.errors import UnauthenticatedError
from src.users.models import SQLAlchemyUser
from src.users.repositories import SQLAlchemyUserRepository
from src.users.schemas import PydanticUserPersonal
from src.users.services import UserService
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
    def built_user(self) -> PydanticUserPersonal:
        return PydanticUserPersonal(name=EXAMPLES.first_name(), key=EXAMPLES.uuid4())

    @pytest_asyncio.fixture
    async def user_and_raw_key(self) -> tuple[SQLAlchemyUser, UUID]:
        raw_key = EXAMPLES.uuid4()
        key = sha256(str(raw_key).encode()).hexdigest()
        user_ = await self.factory_(key=key)

        return user_, raw_key

    @pytest_asyncio.fixture
    async def followers(self) -> tuple[SQLAlchemyUser, SQLAlchemyUser]:
        user_1, user_2 = await self.factory_.create_batch(2)
        await self.test_service.follow(user_1.id, user_2.id)

        return user_1, user_2

    @pytest.mark.asyncio
    async def test_get_by_key(
        self, user_and_raw_key: tuple[SQLAlchemyUser, UUID]
    ) -> None:
        user, raw_key = user_and_raw_key

        assert user.name == (await self.test_service.authenticate(raw_key)).name

    @pytest.mark.asyncio
    async def test_get_by_nonexistent_key(
        self, user_and_raw_key: tuple[SQLAlchemyUser, UUID]
    ) -> None:
        with pytest.raises(UnauthenticatedError):
            await self.test_service.authenticate(EXAMPLES.uuid4())

    @pytest.mark.asyncio
    async def test_get_by_id(self, user: SQLAlchemyUser) -> None:
        assert user.name == (await self.test_service.find_by_id(user.id)).name

    @pytest.mark.asyncio
    async def test_get_by_nonexistent_id(self, user: SQLAlchemyUser) -> None:
        with pytest.raises(NotFoundError):
            await self.test_service.find_by_id(EXAMPLES.uuid4())

    @pytest.mark.asyncio
    async def test_create(self, built_user: PydanticUserPersonal) -> None:
        assert built_user.name == (await self.test_service.sign_up(built_user)).name

    @pytest.mark.asyncio
    async def test_follow(
        self, followers: tuple[SQLAlchemyUser, SQLAlchemyUser]
    ) -> None:
        user_1, user_2 = followers

        assert await user_1.awaitable_attrs.followers == [user_2]
        assert await user_2.awaitable_attrs.following == [user_1]

    @pytest.mark.asyncio
    async def test_follow_self(self, user: SQLAlchemyUser) -> None:
        with pytest.raises(SelfActionError):
            await self.test_service.follow(user.id, user.id)

    @pytest.mark.asyncio
    async def test_unfollow(
        self, followers: tuple[SQLAlchemyUser, SQLAlchemyUser]
    ) -> None:
        user_1, user_2 = followers
        await self.test_service.unfollow(user_1.id, user_2.id)

        assert await user_1.awaitable_attrs.followers == []
        assert await user_2.awaitable_attrs.following == []

    @pytest.mark.asyncio
    async def test_unfollow_self(self, user: SQLAlchemyUser) -> None:
        await self.test_service.unfollow(user.id, user.id)

    @pytest.mark.asyncio
    async def test_unfollow_nonexistent(
        self, followers: tuple[SQLAlchemyUser, SQLAlchemyUser]
    ) -> None:
        user_1, user_2 = followers

        await self.test_service.unfollow(user_1.id, user_2.id)
