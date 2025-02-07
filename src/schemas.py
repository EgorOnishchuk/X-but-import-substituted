"""
Схемы валидации и сериализации данных уровня приложения.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

ID = Annotated[
    UUID,
    Path(
        alias="id",
        description="Уникальный идентификатор",
        example="9b4b9b4b-9b4b-9b4b-9b4b-9b4b9b4b9b4b",
    ),
]


class Schema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class Error(Schema):
    msg: Annotated[str, Field(example="Something went wrong.")]
