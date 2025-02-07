"""
Схемы валидации пользователей.
"""

from typing import Annotated
from uuid import UUID

from pydantic import Field

from src.schemas import Schema


class User(Schema):
    name: Annotated[
        str,
        Field(
            min_length=1, max_length=30, description="Имя пользователя", example="Иван"
        ),
    ]


class UserNotDetailed(User):
    id: Annotated[
        UUID,
        Field(
            description="Уникальный идентификатор",
            example="4b0e9c4b-9b4e-4b4b-9b4b-9b4b9b4b9b4b",
        ),
    ]


class UserDetailed(UserNotDetailed):
    followers: list["UserNotDetailed"]
    following: list["UserNotDetailed"]


class UserPersonal(User):
    key: Annotated[
        UUID,
        Field(description="Ключ API", example="89b4b9b4-9b4b-9b4b-9b4b-9b4b9b4b9b4b"),
    ]


class UserSafe(User):
    key: Annotated[str, Field(min_length=64, max_length=64)]
