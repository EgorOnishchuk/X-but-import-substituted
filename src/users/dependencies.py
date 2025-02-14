"""
Сюда относятся не только зависимости самой сущности пользователя, но и системы авторизации.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader

from src.dependencies import Session
from src.users.errors import UnauthenticatedError
from src.users.repositories import SQLAlchemyUserRepository
from src.users.schemas import PydanticUserDetailed
from src.users.services import UserService

key_header: APIKeyHeader = APIKeyHeader(name="X-API-Key", auto_error=False)


async def _get_key(api_key: Annotated[UUID, Security(key_header)]) -> UUID:
    if api_key is None:
        raise UnauthenticatedError("API key is missing")
    return api_key


def _get_user_service(session: Session) -> UserService:
    return UserService(SQLAlchemyUserRepository(session))


Service = Annotated[UserService, Depends(_get_user_service)]


async def _authenticate(
    key: Annotated[UUID, Security(_get_key)], service: Service
) -> PydanticUserDetailed:
    return await service.authenticate(key)


CurrentUser = Annotated[PydanticUserDetailed, Security(_authenticate)]
