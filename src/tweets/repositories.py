from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.repositories import SQLAlchemyRepository
from src.schemas import dto_from_obj, obj_from_dto
from src.tweets.models import SQLAlchemyTweet, sqlalchemy_likes
from src.tweets.schemas import (
    PydanticTweetDetailed,
    PydanticTweetID,
    PydanticTweetPersonal,
    PydanticTweetsDetailed,
    TweetDetailed,
    TweetID,
    TweetsDetailed,
)
from src.users.models import SQLAlchemyUser, sqlalchemy_follows


class TweetRepository(ABC):
    @dto_from_obj(TweetDetailed)
    @abstractmethod
    async def get_by_id(self, id_: UUID) -> Any:
        pass

    @dto_from_obj(TweetsDetailed)
    @abstractmethod
    async def get_all(self, user_id: UUID) -> Sequence[Any]:
        pass

    @dto_from_obj(TweetID)
    @abstractmethod
    async def create(self, tweet: PydanticTweetPersonal) -> Any:
        pass

    @abstractmethod
    async def delete(self, tweet_id: UUID) -> None:
        pass

    @abstractmethod
    async def create_like(self, tweet_id: UUID, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def delete_like(self, tweet_id: UUID, user_id: UUID) -> None:
        pass


class SQLAlchemyTweetRepository(SQLAlchemyRepository, TweetRepository):
    @dto_from_obj(PydanticTweetDetailed)
    async def get_by_id(self, id_: UUID) -> SQLAlchemyTweet:
        return await self._get_by_id(
            id_, SQLAlchemyTweet, (SQLAlchemyTweet.author, SQLAlchemyTweet.likes)
        )

    @dto_from_obj(PydanticTweetsDetailed)
    async def get_all(self, user_id: UUID) -> Sequence[SQLAlchemyTweet]:
        return (
            (
                await self._session.execute(
                    select(SQLAlchemyTweet)
                    .outerjoin(sqlalchemy_likes)
                    .join(
                        SQLAlchemyUser, SQLAlchemyTweet.author_id == SQLAlchemyUser.id
                    )
                    .join(
                        sqlalchemy_follows,
                        sqlalchemy_follows.c.followed_id == SQLAlchemyTweet.author_id,
                    )
                    .where(sqlalchemy_follows.c.follower_id == user_id)
                    .group_by(SQLAlchemyTweet.id)
                    .order_by(func.count(sqlalchemy_likes.c.user_id).desc())
                    .options(
                        selectinload(SQLAlchemyTweet.likes),
                        selectinload(SQLAlchemyTweet.author),
                    )
                )
            )
            .scalars()
            .all()
        )

    @dto_from_obj(PydanticTweetID)
    @obj_from_dto(SQLAlchemyTweet)
    async def create(self, tweet: PydanticTweetPersonal) -> SQLAlchemyTweet:
        return await self._create(tweet)

    async def delete(self, tweet_id: UUID) -> None:
        await self._delete_by_id(
            tweet_id,
            SQLAlchemyTweet,
            (
                SQLAlchemyTweet.author,
                SQLAlchemyTweet.likes,
            ),
        )

    async def create_like(self, tweet_id: UUID, user_id: UUID) -> None:
        tweet = await self._get_by_id(
            tweet_id,
            SQLAlchemyTweet,
            (
                SQLAlchemyTweet.author,
                SQLAlchemyTweet.likes,
            ),
        )

        await self._append_related_by_id(
            tweet.likes,
            user_id,
            SQLAlchemyUser,
            (SQLAlchemyUser.following, SQLAlchemyUser.followers),
        )

    async def delete_like(self, tweet_id: UUID, user_id: UUID) -> None:
        tweet = await self._get_by_id(
            tweet_id,
            SQLAlchemyTweet,
            (
                SQLAlchemyTweet.author,
                SQLAlchemyTweet.likes,
            ),
        )

        await self._remove_related_by_id(
            tweet.likes,
            user_id,
            SQLAlchemyUser,
            (SQLAlchemyUser.following, SQLAlchemyUser.followers),
        )
