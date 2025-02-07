from typing import Type
from uuid import uuid4

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

from src.tweets.models import SQLAlchemyTweet
from src.users.models import SQLAlchemyUser


class SQLAlchemyUserFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model: Type[SQLAlchemyUser] = SQLAlchemyUser

    name: factory.Faker = factory.Faker("first_name")
    key: factory.Faker = factory.Faker("sha256")


class SQLAlchemyTweetFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model: Type[SQLAlchemyTweet] = SQLAlchemyTweet

    text: factory.Faker = factory.Faker("sentence")
    medias: factory.LazyFunction = factory.LazyFunction(
        lambda: [uuid4() for _ in range(3)]
    )
    author: factory.SubFactory = factory.SubFactory(SQLAlchemyUserFactory)
