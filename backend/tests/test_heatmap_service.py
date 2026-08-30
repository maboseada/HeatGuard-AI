"""Tests for HeatmapService — payload construction and validation."""
import pytest
from unittest.mock import AsyncMock
from app.services.fortyguard.heatmap import HeatmapService
from app.services.fortyguard.client import FortyGuardClient, FortyGuardAPIError


SAMPLE_POLYGON = [
    [
        [-74.0170, 40.7050],
        [-74.0030, 40.7050],
        [-74.0030, 40.7180],
        [-74.0170, 40.7180],
        [-74.0170, 40.7050],
    ]
]

SAMPLE_DATE_TIME = {
    "start_date": "2024-07-15",
    "start_time": "14:00",
    "filter_type": 1,
}


class TestHeatmapSubmission:
    @pytest.mark.asyncio
    async def test_successful_submission_returns_activity_id(
        self, mock_fg_client, fg_success_heatmap_response
    ):
        mock_fg_client.post.return_value = fg_success_heatmap_response
        service = HeatmapService(mock_fg_client)

        activity_id = await service.submit(
            polygon_coordinates=SAMPLE_POLYGON,
            date_time=SAMPLE_DATE_TIME,
            granularity=100,
        )
        assert activity_id == "test-activity-uuid-123"

    @pytest.mark.asyncio
    async def test_payload_uses_polygon_aoi_feature_collection(
        self, mock_fg_client, fg_success_heatmap_response
    ):
        """The POST payload must wrap coordinates in a FeatureCollection."""
        mock_fg_client.post.return_value = fg_success_heatmap_response
        service = HeatmapService(mock_fg_client)

        await service.submit(
            polygon_coordinates=SAMPLE_POLYGON,
            date_time=SAMPLE_DATE_TIME,
            granularity=100,
        )

        # Inspect the payload sent to the client
        call_args = mock_fg_client.post.call_args
        payload = call_args[1]["json"]

        assert "polygon_aoi" in payload
        assert payload["polygon_aoi"]["type"] == "FeatureCollection"
        assert payload["polygon_aoi"]["features"][0]["type"] == "Feature"
        assert (
            payload["polygon_aoi"]["features"][0]["geometry"]["type"] == "Polygon"
        )
        assert (
            payload["polygon_aoi"]["features"][0]["geometry"]["coordinates"]
            == SAMPLE_POLYGON
        )

    @pytest.mark.asyncio
    async def test_granularity_60_accepted(
        self, mock_fg_client, fg_success_heatmap_response
    ):
        mock_fg_client.post.return_value = fg_success_heatmap_response
        service = HeatmapService(mock_fg_client)
        activity_id = await service.submit(SAMPLE_POLYGON, SAMPLE_DATE_TIME, 60)
        assert activity_id is not None

    @pytest.mark.asyncio
    async def test_granularity_80_accepted(
        self, mock_fg_client, fg_success_heatmap_response
    ):
        mock_fg_client.post.return_value = fg_success_heatmap_response
        service = HeatmapService(mock_fg_client)
        activity_id = await service.submit(SAMPLE_POLYGON, SAMPLE_DATE_TIME, 80)
        assert activity_id is not None

    @pytest.mark.asyncio
    async def test_invalid_granularity_raises_value_error(self, mock_fg_client):
        service = HeatmapService(mock_fg_client)
        with pytest.raises(ValueError, match="Granularity must be 60, 80, or 100"):
            await service.submit(SAMPLE_POLYGON, SAMPLE_DATE_TIME, 50)

    @pytest.mark.asyncio
    async def test_invalid_granularity_200_raises(self, mock_fg_client):
        service = HeatmapService(mock_fg_client)
        with pytest.raises(ValueError):
            await service.submit(SAMPLE_POLYGON, SAMPLE_DATE_TIME, 200)

    @pytest.mark.asyncio
    async def test_optional_analytic_type_included(
        self, mock_fg_client, fg_success_heatmap_response
    ):
        mock_fg_client.post.return_value = fg_success_heatmap_response
        service = HeatmapService(mock_fg_client)

        await service.submit(
            SAMPLE_POLYGON, SAMPLE_DATE_TIME, 100, analytic_type="tcm"
        )

        payload = mock_fg_client.post.call_args[1]["json"]
        assert payload["analytic_type"] == "tcm"

    @pytest.mark.asyncio
    async def test_optional_threshold_and_direction(
        self, mock_fg_client, fg_success_heatmap_response
    ):
        mock_fg_client.post.return_value = fg_success_heatmap_response
        service = HeatmapService(mock_fg_client)

        await service.submit(
            SAMPLE_POLYGON,
            SAMPLE_DATE_TIME,
            100,
            analytic_type="exceedance",
            threshold=35.0,
            direction="above",
        )

        payload = mock_fg_client.post.call_args[1]["json"]
        assert payload["threshold"] == 35.0
        assert payload["direction"] == "above"

    @pytest.mark.asyncio
    async def test_no_activity_id_in_response_raises(self, mock_fg_client):
        mock_fg_client.post.return_value = {
            "error": False,
            "data": {},
        }
        service = HeatmapService(mock_fg_client)

        with pytest.raises(FortyGuardAPIError, match="No activity_id"):
            await service.submit(SAMPLE_POLYGON, SAMPLE_DATE_TIME, 100)

    @pytest.mark.asyncio
    async def test_error_response_raises(self, mock_fg_client):
        mock_fg_client.post.return_value = {
            "error": True,
            "message": "Invalid polygon",
        }
        service = HeatmapService(mock_fg_client)

        with pytest.raises(FortyGuardAPIError, match="Invalid polygon"):
            await service.submit(SAMPLE_POLYGON, SAMPLE_DATE_TIME, 100)
