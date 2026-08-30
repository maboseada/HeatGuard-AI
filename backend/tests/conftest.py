import os
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Set test environment variables BEFORE any app imports
os.environ["FORTYGUARD_API_KEY"] = "test_key_not_real"
os.environ["FORTYGUARD_BASE_URL"] = "https://api.fortyguard.com/v1"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["POLL_INTERVAL_SECONDS"] = "1"
os.environ["MAX_POLL_ATTEMPTS"] = "3"

from app.db.database import Base
from app.services.fortyguard.client import FortyGuardClient


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    session_factory = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
def mock_fg_client():
    """A mock FortyGuardClient that doesn't make real HTTP calls."""
    client = AsyncMock(spec=FortyGuardClient)
    client.base_url = "https://api.fortyguard.com/v1"
    client.api_key = "test_key_not_real"
    client.timeout = 30
    return client


@pytest.fixture
def fg_success_heatmap_response():
    """Standard successful heatmap submission response from FortyGuard."""
    return {
        "error": False,
        "status_code": 200,
        "message": "Heatmap Submitted Successfully",
        "data": {"activity_id": "test-activity-uuid-123"},
    }


@pytest.fixture
def fg_success_env_response():
    """Standard successful environmental submission response from FortyGuard."""
    return {
        "error": False,
        "status_code": 200,
        "message": "Environmental Parameters Submitted Successfully",
        "data": {"activity_id": "test-env-activity-uuid-456"},
    }


@pytest.fixture
def fg_processing_status():
    return {
        "error": False,
        "status_code": 200,
        "message": "Processing",
        "data": {"activity_id": "test-activity-uuid-123", "status": "Processing"},
    }


@pytest.fixture
def fg_completed_status():
    return {
        "error": False,
        "status_code": 200,
        "message": "Completed",
        "data": {
            "activity_id": "test-activity-uuid-123",
            "status": "Completed",
            "result": {
                "heat_index_celsius": 38.5,
                "apparent_temperature_celsius": 37.1,
                "wet_bulb_temperature_celsius": 28.3,
                "relative_humidity_percent": 65.0,
                "solar_irradiance": 850.0,
            },
        },
    }


@pytest.fixture
def fg_failed_status():
    return {
        "error": False,
        "status_code": 200,
        "message": "Failed",
        "data": {
            "activity_id": "test-activity-uuid-123",
            "status": "Failed",
        },
    }
