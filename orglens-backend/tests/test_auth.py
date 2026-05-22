import pytest
import pytest_asyncio
import asyncio
import uuid

from typing import AsyncGenerator, Generator
from datetime import timedelta

from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.main import app
from app.database import Base, get_db
from app.models.auth import User

from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
)

# =============================================================================
# POSTGRES TEST DATABASE
# =============================================================================

TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/orglens_test"
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# =============================================================================
# EVENT LOOP
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:

    loop = asyncio.new_event_loop()

    yield loop

    loop.close()


# =============================================================================
# DATABASE FIXTURE
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# =============================================================================
# CLIENT FIXTURE
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:

        yield ac

    app.dependency_overrides.clear()


# =============================================================================
# TEST USER FIXTURE
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def test_user(
    db_session: AsyncSession,
) -> User:

    user = User(
        id=uuid.UUID(
            "11111111-1111-1111-1111-111111111111"
        ),

        email="test@example.com",

        hashed_password=hash_password(
            "TestPassword123!"
        ),

        full_name="Test User",

        is_active=True,
    )

    db_session.add(user)

    await db_session.commit()

    await db_session.refresh(user)

    return user


# =============================================================================
# AUTH HEADERS FIXTURE
# =============================================================================

@pytest_asyncio.fixture
async def auth_headers(
    test_user: User,
):

    token = create_access_token(
        {"sub": str(test_user.id)}
    )

    return {
        "Authorization": f"Bearer {token}"
    }


# =============================================================================
# ASYNCIO MARK
# =============================================================================

pytestmark = pytest.mark.asyncio