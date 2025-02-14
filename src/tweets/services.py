from uuid import UUID

from src.errors import NotFoundError, SelfActionError
from src.tweets.repositories import TweetRepository
from src.tweets.schemas import (
    PydanticTweetID,
    PydanticTweetPersonal,
    PydanticTweetsDetailed,
)
from src.users.errors import UnauthorizedError


class TweetService:
    def __init__(self, repository: TweetRepository) -> None:
        self._repository: TweetRepository = repository

    async def get_list(self, user_id: UUID) -> PydanticTweetsDetailed:
        return await self._repository.get_all(user_id)

    async def publish(self, tweet: PydanticTweetPersonal) -> PydanticTweetID:
        return await self._repository.create(tweet)

    async def remove(self, id_: UUID, author_id: UUID) -> None:
        try:
            tweet = await self._repository.get_by_id(id_)
        except NotFoundError:
            return
        self._check_owned(tweet.author.id, author_id)

        await self._repository.delete(id_)

    async def like(self, tweet_id: UUID, user_id: UUID) -> None:
        tweet = await self._repository.get_by_id(tweet_id)
        self._check_not_owned(tweet.author.id, user_id)

        await self._repository.create_like(tweet_id, user_id)

    async def unlike(self, tweet_id: UUID, user_id: UUID) -> None:
        await self._repository.delete_like(tweet_id, user_id)

    @staticmethod
    def _check_owned(tweet_author_id: UUID, current_author_id: UUID) -> None:
        if tweet_author_id != current_author_id:
            raise UnauthorizedError("It's not your tweet.")

    @staticmethod
    def _check_not_owned(tweet_author_id: UUID, current_author_id: UUID) -> None:
        if tweet_author_id == current_author_id:
            raise SelfActionError("It's your own tweet.")
