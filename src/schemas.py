"""
Схемы валидации и сериализации данных могут также выполнять роль DTO.
"""

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Annotated, Any, Self, Type, TypeVar
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.alias_generators import to_camel

from src.settings import EXAMPLES


class Schema(ABC):
    @abstractmethod
    def to_dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def from_obj(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        pass


class PydanticSchema(BaseModel, Schema):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    def to_dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self.model_dump(*args, **kwargs)

    @classmethod
    def from_obj(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        return cls.model_validate(obj, *args, **kwargs)


class PydanticRootSchema(RootModel, PydanticSchema):
    pass


SchemaT = TypeVar("SchemaT", bound=Schema)
FuncT = TypeVar("FuncT", bound=Callable[..., Awaitable[Any]])


def dto_from_obj(dto_class: Type[SchemaT]) -> Callable[[FuncT], FuncT]:
    def decorator(func: FuncT) -> FuncT:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> SchemaT:
            obj = await func(self, *args, **kwargs)
            return dto_class.from_obj(obj)

        return wrapper

    return decorator


def obj_from_dto(obj_class: Type[Any]) -> Callable[[FuncT], FuncT]:
    def decorator(func: FuncT) -> FuncT:
        @wraps(func)
        async def wrapper(self, dto: Schema, *args, **kwargs) -> Any:
            obj = obj_class(**dto.to_dict())
            return await func(self, obj, *args, **kwargs)

        return wrapper

    return decorator


class Error(Schema):
    msg: Any


class PydanticError(PydanticSchema, Error):
    msg: Annotated[str, Field(examples=["Something went wrong."])]


ID = Annotated[
    UUID,
    Path(
        alias="id",
        description="Уникальный идентификатор",
        examples=[EXAMPLES.uuid4()],
    ),
]
