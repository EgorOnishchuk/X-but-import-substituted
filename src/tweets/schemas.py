from typing import Annotated, Any
from uuid import UUID

from pydantic import Field

from src.schemas import PydanticRootSchema, PydanticSchema, Schema
from src.settings import EXAMPLES
from src.users.schemas import PydanticUserNotDetailed


class TweetID(Schema):
    id: Any


class PydanticTweetID(PydanticSchema, TweetID):
    id: Annotated[
        UUID,
        Field(
            description="Уникальный идентификатор",
            examples=[EXAMPLES.uuid4()],
        ),
    ]


class TweetNotDetailed(Schema):
    text: Any
    medias: Any


class PydanticTweetNotDetailed(PydanticSchema, TweetNotDetailed):
    text: Annotated[
        str,
        Field(
            min_length=1,
            max_length=500,
            description="Текст",
            examples=[EXAMPLES.text(20)],
        ),
    ]
    medias: Annotated[
        list[UUID],
        Field(
            description="Медиафайлы",
            examples=[[EXAMPLES.uuid4()]],
        ),
    ]


class TweetPersonal(TweetNotDetailed):
    author_id: Any


class PydanticTweetPersonal(PydanticTweetNotDetailed, TweetPersonal):
    author_id: Annotated[
        UUID, Field(description="Уникальный идентификатор", examples=[EXAMPLES.uuid4()])
    ]


class TweetDetailed(TweetID, TweetNotDetailed):
    author: Any
    likes: Any


class PydanticTweetDetailed(PydanticTweetID, PydanticTweetNotDetailed, TweetDetailed):
    author: PydanticUserNotDetailed
    likes: list[PydanticUserNotDetailed]


class TweetsDetailed(Schema):
    root: Any


class PydanticTweetsDetailed(PydanticRootSchema, TweetsDetailed):
    root: list[PydanticTweetDetailed]
