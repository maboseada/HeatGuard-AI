"""Tests for API routes — health, sites, jobs endpoints."""
import os
import pytest
import uuid

# Ensure test env is set before app import
os.environ.setdefault("FORTYGUARD_API_KEY", "test_key")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import init_db


@pytest.fixture(autouse=True)
async def setup_db():
    """Initialize database tables before API tests."""
    await init_db()
    yield


@pytest.mark.asyncio
async def test_health_endpoint():
    """GET /health returns healthy status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_create_site():
    """POST /api/sites creates a new site."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/sites",
            json={
                "name": "Test Site",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "description": "A test industrial zone",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Site"
    assert data["latitude"] == 40.7128
    assert "id" in data


@pytest.mark.asyncio
async def test_list_sites():
    """GET /api/sites returns a list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/sites")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_site_not_found():
    """GET /api/sites/{id} returns 404 for nonexistent site."""
    transport = ASGITransport(app=app)
    fake_id = str(uuid.uuid4())
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/sites/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Site not found"


@pytest.mark.asyncio
async def test_get_job_not_found():
    """GET /api/jobs/{id} returns 404 for nonexistent job."""
    transport = ASGITransport(app=app)
    fake_id = str(uuid.uuid4())
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/jobs/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


@pytest.mark.asyncio
async def test_create_site_validation_error():
    """POST /api/sites with missing required fields returns 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/sites",
            json={"name": "Missing coords"},
        )
    assert response.status_code == 422
