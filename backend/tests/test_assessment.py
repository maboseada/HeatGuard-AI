import pytest
import uuid
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import init_db
from app.models.site import Site
from app.schemas.assessment import AssessmentRequest, AssessmentMode, AssessmentStatus, DataProvenance
from app.services.jobs.assessment_manager import AssessmentManager


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield


@pytest.mark.asyncio
async def test_demo_assessment_instant_completion(async_session, mock_fg_client):
    # 1. Create a test site
    site_id = uuid.uuid4()
    site = Site(
        id=site_id,
        name="Dubai Test Site",
        latitude=25.2048,
        longitude=55.2708
    )
    async_session.add(site)
    await async_session.commit()

    manager = AssessmentManager()
    req = AssessmentRequest(mode=AssessmentMode.DEMO)

    record = await manager.run_assessment(async_session, site_id, req, mock_fg_client)
    assert record.status == AssessmentStatus.COMPLETED.value
    assert record.mode == AssessmentMode.DEMO.value
    assert record.map_geojson is not None
    assert record.environmental is not None
    assert record.environmental["provenance"] == DataProvenance.DEMO_SYNTHETIC.value
    assert record.stats["provenance"] == DataProvenance.DEMO_SYNTHETIC.value


@pytest.mark.asyncio
async def test_live_assessment_submission_and_polling(async_session, mock_fg_client):
    site_id = uuid.uuid4()
    site = Site(
        id=site_id,
        name="Live Test Site",
        latitude=40.7128,
        longitude=-74.0060
    )
    async_session.add(site)
    await async_session.commit()

    manager = AssessmentManager()
    req = AssessmentRequest(mode=AssessmentMode.LIVE)

    with patch("app.services.fortyguard.heatmap.HeatmapService.submit", new_callable=AsyncMock, return_value="act-hm-123"), \
         patch("app.services.fortyguard.environmental.EnvironmentalService.submit", new_callable=AsyncMock, return_value="act-env-456"), \
         patch.object(manager, "_poll_live_assessment", new_callable=AsyncMock):

        record = await manager.run_assessment(async_session, site_id, req, mock_fg_client)
        assert record.status == AssessmentStatus.PROCESSING.value
        assert record.mode == AssessmentMode.LIVE.value
        assert record.heatmap_activity_id == "act-hm-123"
        assert record.env_activity_id == "act-env-456"


@pytest.mark.asyncio
async def test_assess_endpoint_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create site first
        site_res = await ac.post("/api/sites", json={
            "name": "API Assessment Site",
            "latitude": 25.0,
            "longitude": 55.0
        })
        site_id = site_res.json()["id"]

        # Run DEMO assessment
        assess_res = await ac.post(f"/api/sites/{site_id}/assess", json={
            "mode": "DEMO"
        })
        assert assess_res.status_code == 200
        data = assess_res.json()
        assert data["status"] == "Completed"
        assert data["mode"] == "DEMO"
        assert data["environmental"]["provenance"] == "demo_synthetic"
        assert data["stats"]["provenance"] == "demo_synthetic"
        assert "map_geojson" in data

        # Get latest assessment
        latest_res = await ac.get(f"/api/sites/{site_id}/assessment/latest")
        assert latest_res.status_code == 200
        assert latest_res.json()["id"] == data["id"]
