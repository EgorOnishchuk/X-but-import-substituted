from typing import Annotated

from pydantic import Field
from typing_extensions import Any

from src.schemas import PydanticSchema, Schema
from src.settings import EXAMPLES


class Media(Schema):
    name: Any


class PydanticMedia(PydanticSchema):
    name: Annotated[
        str,
        Field(
            description="Имя файла с расширением",
            examples=[f"{EXAMPLES.uuid4()}.{EXAMPLES.file_extension('image')}"],
        ),
    ]
