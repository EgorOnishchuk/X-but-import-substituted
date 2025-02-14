from abc import ABC
from typing import Any, Type

import pytest
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import SQLAlchemyRepository


class TestModel(ABC):
    service: Any
    repository: Any


class TestSQLAlchemyModel(TestModel):
    factory_: Type[AsyncSQLAlchemyFactory]
    repository: Type[SQLAlchemyRepository]

    @pytest.fixture(autouse=True)
    def set_service(self, session: AsyncSession) -> None:
        self.test_service = self.service(self.repository(session))
