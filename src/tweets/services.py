"""
Слой логики операций с публикациями (твитами).
"""

from abc import abstractmethod
from contextlib import suppress
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.errors import NotFoundError, SelfActionError
from src.services import DBRepository, SQLAlchemyRepository
from src.tweets.models import DataTweet, SQLAlchemyTweet, sqlalchemy_likes
from src.tweets.schemas import TweetNotDetailed
from src.users.errors import UnauthorizedError
from src.users.models import DataUser, SQLAlchemyUser, sqlalchemy_follows


class TweetRepository(DBRepository):
    @abstractmethod
    async def get_by_id(self, id_: UUID) -> DataTweet:
        """
        Получает публикацию по ID.
        :param id_: Уникальный идентификатор.
        :return: Публикация.
        """

    @abstractmethod
    async def get_all(self, user_id: UUID) -> list[DataTweet]:
        """
        Получает все публикации от отслеживаемых пользователей.
        :return: Список публикаций.
        """

    @abstractmethod
    async def create(self, tweet: TweetNotDetailed, author_id: UUID) -> DataTweet:
        """
        Создаёт публикацию.
        :param tweet: Публикация.
        :param author_id: ID пользователя, создающего публикацию.
        :return: Публикация.
        """

    @abstractmethod
    async def delete(self, tweet: DataTweet) -> None:
        """
        Удаляет публикацию.
        :param tweet: Публикация.
        """

    @abstractmethod
    async def create_like(self, tweet: DataTweet, user: DataUser) -> None:
        """
        Создаёт отметку «нравится» для публикации.
        :param tweet: Понравившаяся публикация.
        :param user: Пользователь.
        """

    @abstractmethod
    async def delete_like(self, tweet: DataTweet, user: DataUser) -> None:
        """
        Удаляет отметку «нравится» для публикации.
        :param tweet: Понравившаяся публикация.
        :param user: Пользователь.
        """


class SQLAlchemyTweetRepository(SQLAlchemyRepository, TweetRepository):
    async def get_by_id(self, id_: UUID) -> SQLAlchemyTweet:
        return await self._get_by_id(
            SQLAlchemyTweet, id_, (SQLAlchemyTweet.author, SQLAlchemyTweet.likes)
        )

    async def get_all(self, user_id: UUID) -> list[SQLAlchemyTweet]:
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
                    .options(selectinload(SQLAlchemyTweet.likes))
                )
            )
            .scalars()
            .all()
        )

    async def create(self, tweet: TweetNotDetailed, author_id: UUID) -> SQLAlchemyTweet:
        return await self._create(
            dict(**tweet.model_dump(), author_id=author_id), SQLAlchemyTweet
        )

    async def delete(self, tweet: SQLAlchemyTweet) -> None:
        await self._delete(tweet)

    async def create_like(self, tweet: SQLAlchemyTweet, user: SQLAlchemyUser) -> None:
        await self._append_related(tweet.likes, user)

    async def delete_like(self, tweet: SQLAlchemyTweet, user: SQLAlchemyUser) -> None:
        await self._remove_related(tweet.likes, user)


class TweetService:
    """
    Сервис для работы с публикациями.
    """

    def __init__(self, repository: TweetRepository) -> None:
        self._repository: TweetRepository = repository

    async def get_all(self, user: DataUser) -> list[DataTweet]:
        """
        Получает все публикации от отслеживаемых пользователей.
        :return: Список публикаций.
        """
        return await self._repository.get_all(user.id)

    async def create(self, tweet: TweetNotDetailed, author_id: UUID) -> DataTweet:
        """
        Создаёт публикацию.
        :param tweet: Публикация.
        :param author_id: ID пользователя, создающего публикацию.
        :return: Публикация.
        """
        return await self._repository.create(tweet, author_id)

    async def delete(self, id_: UUID, author_id: UUID) -> None:
        """
        Удаляет публикацию.
        :param id_: Уникальный идентификатор.
        :param author_id: ID пользователя, создающего публикацию.
        """
        with suppress(NotFoundError):
            db_tweet = await self._repository.get_by_id(id_)
            self._check_owned(db_tweet.author_id, author_id)
            await self._repository.delete(db_tweet)

    async def create_like(self, tweet_id: UUID, user: DataUser) -> None:
        """
        Создаёт отметку «нравится» для публикации.
        :param tweet_id: ID понравившейся публикации.
        :param user: Пользователь.
        """
        db_tweet = await self._repository.get_by_id(tweet_id)
        self._check_not_owned(db_tweet, user.id)

        await self._repository.create_like(db_tweet, user)

    async def delete_like(self, tweet_id: UUID, user: DataUser) -> None:
        """
        Удаляет отметку «нравится» для публикации.
        :param tweet_id: ID понравившейся публикации.
        :param user: Пользователь.
        """
        db_tweet = await self._repository.get_by_id(tweet_id)

        await self._repository.delete_like(db_tweet, user)

    @staticmethod
    def _check_owned(tweet_id: UUID, author_id: UUID) -> None:
        if tweet_id != author_id:
            raise UnauthorizedError("It's not your tweet.")

    @staticmethod
    def _check_not_owned(tweet: DataTweet, author_id: UUID) -> None:
        pass
        if tweet.author_id == author_id:
            raise SelfActionError("It's your own tweet.")
