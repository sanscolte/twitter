from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from fastapi.testclient import TestClient

from config import (
    TEST_DB_USER,
    TEST_DB_PASS,
    TEST_DB_HOST,
    TEST_DB_PORT,
    TEST_DB_NAME,
)
from database import get_async_session
from main import app
from src.api.models import Base, User

TEST_DATABASE_URL: str = (
    f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}"
    f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)
test_engine: AsyncEngine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)
test_async_session = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор асинхронной сессии для тестирования"""
    async with test_async_session() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session
client = TestClient(app=app)


@pytest.fixture(autouse=True, scope="session")
async def prepare_database() -> None:  # type: ignore
    await drop_test_db_and_tables()
    await create_test_db_and_tables()
    await create_test_db_data()
    yield
    await drop_test_db_and_tables()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
            transport=ASGITransport(app=app),  # type: ignore
            base_url="http://test/api",
            headers={"api-key": "test"},
    ) as ac:
        yield ac


async def create_test_db_and_tables() -> None:
    """Создание таблиц базы данных для тестирования"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_test_db_and_tables() -> None:
    """Удаление таблиц базы данных для тестирования"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def create_test_db_data() -> None:
    """Наполнение таблиц базы данных для тестирования"""
    async with test_async_session() as session:
        user1: User = User(api_key="test", name="Tony")
        user2: User = User(api_key="test2", name="Mike")
        session.add_all([user1, user2])

        await session.commit()
