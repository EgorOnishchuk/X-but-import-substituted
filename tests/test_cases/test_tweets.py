from typing import Any, Type
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import select

from src.errors import SelfActionError
from src.settings import EXAMPLES
from src.tweets.models import SQLAlchemyTweet
from src.tweets.repositories import SQLAlchemyTweetRepository
from src.tweets.schemas import PydanticTweetPersonal
from src.tweets.services import TweetService
from src.users.errors import UnauthorizedError
from tests.factories import SQLAlchemyTweetFactory
from tests.test_cases.test_model import TestSQLAlchemyModel


class TestSQLAlchemyTweets(TestSQLAlchemyModel):
    factory_: Type[SQLAlchemyTweetFactory] = SQLAlchemyTweetFactory
    service: Type[TweetService] = TweetService
    repository: Type[SQLAlchemyTweetRepository] = SQLAlchemyTweetRepository

    @pytest_asyncio.fixture
    async def tweet(self) -> SQLAlchemyTweet:
        return await self.factory_()

    @pytest_asyncio.fixture
    async def built_tweet(self) -> PydanticTweetPersonal:
        author_id = (await self.factory_()).author_id
        return PydanticTweetPersonal(
            text=EXAMPLES.sentence(),
            medias=[EXAMPLES.uuid4() for _ in range(3)],
            author_id=author_id,
        )

    @pytest_asyncio.fixture
    async def tweets(self) -> list[SQLAlchemyTweet]:
        return await self.factory_.create_batch(2)

    @pytest.mark.asyncio
    async def test_get_all(self, tweet: SQLAlchemyTweet) -> None:
        assert (await self.test_service.get_list(tweet.author.id)).root == []

    @pytest.mark.asyncio
    async def test_create(self, built_tweet: PydanticTweetPersonal) -> None:
        assert isinstance((await self.test_service.publish(built_tweet)).id, UUID)

    @pytest.mark.asyncio
    async def test_delete(self, tweet: SQLAlchemyTweet, session: Any) -> None:
        await self.test_service.remove(tweet.id, tweet.author_id)

        assert (await session.execute(select(SQLAlchemyTweet))).scalars().all() == []

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, tweet: SQLAlchemyTweet) -> None:
        await self.test_service.remove(EXAMPLES.uuid4(), tweet.author_id)

    @pytest.mark.asyncio
    async def test_delete_unowned(self, tweets: list[SQLAlchemyTweet]) -> None:
        tweet_1, author_id_2 = tweets[0], tweets[1].author_id

        with pytest.raises(UnauthorizedError):
            await self.test_service.remove(tweet_1.id, author_id_2)

    @pytest.mark.asyncio
    async def test_like(self, tweets: list[SQLAlchemyTweet]) -> None:
        tweet_1, user_2 = tweets[0], tweets[1].author
        await self.test_service.like(tweet_1.id, user_2.id)

        assert tweet_1.likes == [user_2]

    @pytest.mark.asyncio
    async def test_like_self(self, tweet: SQLAlchemyTweet) -> None:
        with pytest.raises(SelfActionError):
            await self.test_service.like(tweet.id, tweet.author.id)

    @pytest.mark.asyncio
    async def test_unlike(self, tweets: list[SQLAlchemyTweet]) -> None:
        tweet_1, user_2 = tweets[0], tweets[1].author
        await self.test_service.like(tweet_1.id, user_2.id)
        await self.test_service.unlike(tweet_1.id, user_2.id)

        assert await tweet_1.awaitable_attrs.likes == []

    @pytest.mark.asyncio
    async def test_unlike_self(self, tweet: SQLAlchemyTweet) -> None:
        await self.test_service.unlike(tweet.id, tweet.author.id)

    @pytest.mark.asyncio
    async def test_unlike_nonexistent(self, tweets: list[SQLAlchemyTweet]) -> None:
        tweet_1, user_2 = tweets[0], tweets[1].author

        await self.test_service.unlike(tweet_1.id, user_2.id)
