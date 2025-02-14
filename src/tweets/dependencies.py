from typing import Annotated

from fastapi import Depends

from src.dependencies import Session
from src.tweets.repositories import SQLAlchemyTweetRepository
from src.tweets.services import TweetService


def _get_tweet_service(session: Session) -> TweetService:
    return TweetService(SQLAlchemyTweetRepository(session))


Service = Annotated[TweetService, Depends(_get_tweet_service)]
