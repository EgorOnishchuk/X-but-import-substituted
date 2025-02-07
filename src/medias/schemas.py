"""
Схемы медиафайлов.
"""

from typing import Annotated
from uuid import UUID

from pydantic import Field

from src.schemas import Schema


class Media(Schema):
    id: Annotated[
        UUID,
        Field(
            description="Уникальный идентификатор",
            example="4d4d4d4d-4d4d-4d4d-4d4d-4d4d4d4d4d4d",
        ),
    ]
