"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash=get_password_hash("Test123!@#"),
        role=UserRole.USER,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession) -> User:
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        name="Admin User",
        password_hash=get_password_hash("Admin123!@#"),
        role=UserRole.ADMIN,
    )

    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    return admin


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Test123!@#"},
    )
    token_data = response.json()

    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
async def admin_headers(client: AsyncClient, test_admin: User) -> dict:
    """Get authentication headers for admin user."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Admin123!@#"},
    )
    token_data = response.json()

    return {"Authorization": f"Bearer {token_data['access_token']}"}
