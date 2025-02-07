"""
Зависимости публикаций (твитов).
"""

from typing import Annotated

from fastapi import Depends

from src.dependencies import Session
from src.tweets.services import SQLAlchemyTweetRepository, TweetService


def _get_tweet_service(session: Session) -> TweetService:
    return TweetService(SQLAlchemyTweetRepository(session))


Service = Annotated[TweetService, Depends(_get_tweet_service)]
