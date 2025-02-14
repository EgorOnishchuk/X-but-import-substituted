from typing import Type
from uuid import uuid4

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from factory import Sequence
from faker import Faker

from src.tweets.models import SQLAlchemyTweet
from src.users.models import SQLAlchemyUser


class SQLAlchemyUserFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model: Type[SQLAlchemyUser] = SQLAlchemyUser

    name: Sequence = factory.Sequence(lambda n: f"{Faker().first_name()} {n}")
    key: factory.Faker = factory.Faker("sha256")


class SQLAlchemyTweetFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model: Type[SQLAlchemyTweet] = SQLAlchemyTweet

    text: factory.Faker = factory.Faker("sentence")
    medias: factory.LazyFunction = factory.LazyFunction(
        lambda: [uuid4() for _ in range(3)]
    )
    author: factory.SubFactory = factory.SubFactory(SQLAlchemyUserFactory)
