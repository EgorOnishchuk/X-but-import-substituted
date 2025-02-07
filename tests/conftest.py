from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio

from src.db import DBManager
from src.dependencies import get_db_manager
from tests.factories import SQLAlchemyTweetFactory, SQLAlchemyUserFactory


@pytest.fixture
def db_manager() -> DBManager:
    return get_db_manager()


@pytest_asyncio.fixture(autouse=True)
async def operate_tables(db_manager: DBManager) -> AsyncGenerator[Any, None]:
    await db_manager.setup()

    yield

    await db_manager.clear()


@pytest_asyncio.fixture
async def session(db_manager: DBManager) -> Any:
    async with db_manager.get_session() as session:
        yield session


@pytest.fixture(autouse=True)
def set_session(session: Any) -> None:
    for factory in (SQLAlchemyUserFactory, SQLAlchemyTweetFactory):
        factory._meta.sqlalchemy_session = session
