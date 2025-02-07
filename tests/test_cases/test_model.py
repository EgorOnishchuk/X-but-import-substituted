from abc import ABC
from typing import Any, Type
from uuid import UUID, uuid4

import pytest
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import DBRepository, SQLAlchemyRepository


class TestModel(ABC):
    service: Any
    repository: Type[DBRepository]

    @staticmethod
    def get_new_uuid(uuid: UUID) -> UUID:
        while (new_uuid := uuid4()) == uuid:
            new_uuid = uuid4()

        return new_uuid


class TestSQLAlchemyModel(TestModel):
    factory_: Type[AsyncSQLAlchemyFactory]
    repository: Type[SQLAlchemyRepository]

    @pytest.fixture(autouse=True)
    def set_service(self, session: AsyncSession) -> None:
        self.test_service = self.service(self.repository(session))
