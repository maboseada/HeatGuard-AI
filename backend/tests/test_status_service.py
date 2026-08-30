"""Tests for StatusService — polling, completed/failed handling."""
import pytest
from app.services.fortyguard.status import StatusService
from app.services.fortyguard.client import FortyGuardAPIError


class TestStatusPolling:
    @pytest.mark.asyncio
    async def test_processing_status(self, mock_fg_client, fg_processing_status):
        mock_fg_client.get.return_value = fg_processing_status
        service = StatusService(mock_fg_client)

        status, result = await service.check("test-activity-uuid-123")
        assert status == "Processing"
        assert result is None

    @pytest.mark.asyncio
    async def test_completed_status_with_result(
        self, mock_fg_client, fg_completed_status
    ):
        mock_fg_client.get.return_value = fg_completed_status
        service = StatusService(mock_fg_client)

        status, result = await service.check("test-activity-uuid-123")
        assert status == "Completed"
        assert result is not None
        assert result["heat_index_celsius"] == 38.5

    @pytest.mark.asyncio
    async def test_failed_status(self, mock_fg_client, fg_failed_status):
        mock_fg_client.get.return_value = fg_failed_status
        service = StatusService(mock_fg_client)

        status, result = await service.check("test-activity-uuid-123")
        assert status == "Failed"
        assert result is None

    @pytest.mark.asyncio
    async def test_calls_correct_endpoint(self, mock_fg_client, fg_processing_status):
        mock_fg_client.get.return_value = fg_processing_status
        service = StatusService(mock_fg_client)

        await service.check("my-activity-id")

        mock_fg_client.get.assert_called_once_with("/status/my-activity-id")

    @pytest.mark.asyncio
    async def test_error_response_raises(self, mock_fg_client):
        mock_fg_client.get.return_value = {
            "error": True,
            "message": "Activity not found",
        }
        service = StatusService(mock_fg_client)

        with pytest.raises(FortyGuardAPIError, match="Activity not found"):
            await service.check("bad-id")

    @pytest.mark.asyncio
    async def test_missing_status_raises(self, mock_fg_client):
        mock_fg_client.get.return_value = {"error": False, "data": {}}
        service = StatusService(mock_fg_client)

        with pytest.raises(FortyGuardAPIError, match="No status"):
            await service.check("test-id")
