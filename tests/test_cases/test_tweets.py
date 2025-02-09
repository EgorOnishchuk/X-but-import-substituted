from typing import Any, Type
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import select

from src.errors import SelfActionError
from src.tweets.models import SQLAlchemyTweet
from src.tweets.schemas import TweetNotDetailed
from src.tweets.services import SQLAlchemyTweetRepository, TweetService
from src.users.errors import UnauthorizedError
from tests.factories import SQLAlchemyTweetFactory, SQLAlchemyUserFactory
from tests.test_cases.test_model import TestSQLAlchemyModel


class TestSQLAlchemyTweets(TestSQLAlchemyModel):
    factory_: Type[SQLAlchemyTweetFactory] = SQLAlchemyTweetFactory
    service: Type[TweetService] = TweetService
    repository: Type[SQLAlchemyTweetRepository] = SQLAlchemyTweetRepository

    @pytest_asyncio.fixture
    async def tweet(self) -> SQLAlchemyTweet:
        return await self.factory_()

    @pytest_asyncio.fixture
    async def tweet_with_author(self) -> tuple[TweetNotDetailed, UUID]:
        tweet_ = self.factory_.build()
        tweet_ = TweetNotDetailed.model_validate(tweet_)
        author_id = (await SQLAlchemyUserFactory()).id
        return tweet_, author_id

    @pytest_asyncio.fixture
    async def tweets(self) -> list[SQLAlchemyTweet]:
        return await self.factory_.create_batch(2)

    @pytest.mark.asyncio
    async def test_get_all(self, tweet: SQLAlchemyTweet) -> None:
        assert [] == (await self.test_service.get_all(tweet.author))

    @pytest.mark.asyncio
    async def test_create(
        self, tweet_with_author: tuple[TweetNotDetailed, UUID]
    ) -> None:
        tweet_, author_id = tweet_with_author
        db_tweet = await self.test_service.create(tweet_, author_id)

        assert all(
            (
                tweet_.text == db_tweet.text,
                tweet_.medias == db_tweet.medias,
            )
        )

    @pytest.mark.asyncio
    async def test_delete(self, tweet: SQLAlchemyTweet, session: Any) -> None:
        await self.test_service.delete(tweet.id, tweet.author_id)

        assert (await session.execute(select(SQLAlchemyTweet))).scalars().all() == []

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, tweet: SQLAlchemyTweet) -> None:
        await self.test_service.delete(self.get_new_uuid(tweet.id), tweet.author_id)

    @pytest.mark.asyncio
    async def test_delete_unowned(self, tweets: list[SQLAlchemyTweet]) -> None:
        tweet_1, author_id_2 = tweets[0], tweets[1].author_id

        with pytest.raises(UnauthorizedError):
            await self.test_service.delete(tweet_1.id, author_id_2)

    @pytest.mark.asyncio
    async def test_like(self, tweets: list[SQLAlchemyTweet]) -> None:
        tweet_1, user_2 = tweets[0], tweets[1].author
        await self.test_service.create_like(tweet_1.id, user_2)

        assert tweet_1.likes == [user_2]

    @pytest.mark.asyncio
    async def test_like_self(self, tweet: SQLAlchemyTweet) -> None:
        with pytest.raises(SelfActionError):
            await self.test_service.create_like(tweet.id, tweet.author)

    @pytest.mark.asyncio
    async def test_unlike(self, tweets: list[SQLAlchemyTweet]) -> None:
        tweet_1, user_2 = tweets[0], tweets[1].author
        await self.test_service.create_like(tweet_1.id, user_2)
        await self.test_service.delete_like(tweet_1.id, user_2)

        assert tweet_1.likes == []

    @pytest.mark.asyncio
    async def test_unlike_self(self, tweet: SQLAlchemyTweet) -> None:
        await self.test_service.delete_like(tweet.id, tweet.author)
