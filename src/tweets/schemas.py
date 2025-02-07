"""
Схемы публикаций (твитов).
"""

from typing import Annotated
from uuid import UUID

from pydantic import Field

from src.schemas import Schema
from src.users.schemas import UserNotDetailed


class TweetID(Schema):
    id: Annotated[
        UUID,
        Field(
            description="Уникальный идентификатор",
            example="7f7f7f7f-7f7f-7f7f-7f7f-7f7f7f7f7f7f",
        ),
    ]


class TweetNotDetailed(Schema):
    text: Annotated[
        str,
        Field(
            min_length=1,
            max_length=500,
            description="Текст",
            example="Повседневная практика показывает, что "
            "сложившаяся структура организации напрямую "
            "зависит от экономической целесообразности "
            "принимаемых решений.",
        ),
    ]
    medias: Annotated[
        list[UUID],
        Field(
            description="Медиафайлы",
            example=[
                "8f8f8f8f-8f8f-8f8f-8f8f-8f8f8f8f8f8f",
                "5f5f5f5f-5f5f-5f5f-5f5f-5f5f5f5f5f5f",
            ],
        ),
    ]


class TweetDetailed(TweetID, TweetNotDetailed):
    author: UserNotDetailed
    likes: list[UserNotDetailed]
