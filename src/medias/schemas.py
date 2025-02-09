"""
Схемы медиафайлов.
"""

from typing import Annotated

from pydantic import Field

from src.schemas import Schema


class Media(Schema):
    name: Annotated[
        str,
        Field(
            description="Имя файла с расширением",
            example="2b0b0b0b-0b0b-0b0b-0b0b-0b0b0b0b0b0b.png",
        ),
    ]
