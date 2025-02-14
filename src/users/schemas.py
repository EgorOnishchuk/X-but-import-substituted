from typing import Annotated, Any
from uuid import UUID

from pydantic import Field

from src.schemas import PydanticSchema, Schema
from src.settings import EXAMPLES


class User(Schema):
    name: Any


class PydanticUser(PydanticSchema, User):
    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=30,
            description="Имя пользователя",
            examples=[EXAMPLES.first_name()],
        ),
    ]


class UserNotDetailed(User):
    id: Any


class PydanticUserNotDetailed(PydanticUser, UserNotDetailed):
    id: Annotated[
        UUID,
        Field(
            description="Уникальный идентификатор",
            examples=[EXAMPLES.uuid4()],
        ),
    ]


class UserDetailed(UserNotDetailed):
    followers: Any
    following: Any


class PydanticUserDetailed(PydanticUserNotDetailed, UserDetailed):
    followers: list["PydanticUserNotDetailed"]
    following: list["PydanticUserNotDetailed"]


class UserPersonal(User):
    key: Any


class PydanticUserPersonal(PydanticUser, UserPersonal):
    key: Annotated[
        UUID,
        Field(description="Ключ API", examples=[EXAMPLES.uuid4()]),
    ]


class UserSafe(User):
    key: Any


class PydanticUserSafe(PydanticUser, UserSafe):
    key: Annotated[
        str,
        Field(
            min_length=64,
            max_length=64,
            description="Зашифрованный ключ API",
            examples=[EXAMPLES.sha256()],
        ),
    ]
