"""Tests for EnvironmentalService — payload construction, null handling."""
import pytest
from app.services.fortyguard.environmental import EnvironmentalService
from app.services.fortyguard.client import FortyGuardAPIError


SAMPLE_DATE_TIME = {
    "start_date": "2024-07-15",
    "start_time": "14:00",
    "filter_type": 1,
}


class TestEnvironmentalSubmission:
    @pytest.mark.asyncio
    async def test_successful_submission_returns_activity_id(
        self, mock_fg_client, fg_success_env_response
    ):
        mock_fg_client.post.return_value = fg_success_env_response
        service = EnvironmentalService(mock_fg_client)

        activity_id = await service.submit(
            latitude=40.7128,
            longitude=-74.0060,
            temperature=32.5,
            date_time=SAMPLE_DATE_TIME,
        )
        assert activity_id == "test-env-activity-uuid-456"

    @pytest.mark.asyncio
    async def test_payload_has_flat_lat_lng(
        self, mock_fg_client, fg_success_env_response
    ):
        """FortyGuard expects flat latitude/longitude, not nested under 'location'."""
        mock_fg_client.post.return_value = fg_success_env_response
        service = EnvironmentalService(mock_fg_client)

        await service.submit(40.7128, -74.0060, 32.5, SAMPLE_DATE_TIME)

        payload = mock_fg_client.post.call_args[1]["json"]
        assert payload["latitude"] == 40.7128
        assert payload["longitude"] == -74.0060
        assert payload["temperature"] == 32.5
        assert "location" not in payload  # Must NOT be nested

    @pytest.mark.asyncio
    async def test_calls_correct_endpoint(
        self, mock_fg_client, fg_success_env_response
    ):
        mock_fg_client.post.return_value = fg_success_env_response
        service = EnvironmentalService(mock_fg_client)

        await service.submit(40.7128, -74.0060, 32.5, SAMPLE_DATE_TIME)

        mock_fg_client.post.assert_called_once()
        call_args = mock_fg_client.post.call_args
        assert call_args[0][0] == "/env_params"

    @pytest.mark.asyncio
    async def test_error_response_raises(self, mock_fg_client):
        mock_fg_client.post.return_value = {
            "error": True,
            "message": "Invalid coordinates",
        }
        service = EnvironmentalService(mock_fg_client)

        with pytest.raises(FortyGuardAPIError, match="Invalid coordinates"):
            await service.submit(40.7128, -74.0060, 32.5, SAMPLE_DATE_TIME)

    @pytest.mark.asyncio
    async def test_no_activity_id_raises(self, mock_fg_client):
        mock_fg_client.post.return_value = {"error": False, "data": {}}
        service = EnvironmentalService(mock_fg_client)

        with pytest.raises(FortyGuardAPIError, match="No activity_id"):
            await service.submit(40.7128, -74.0060, 32.5, SAMPLE_DATE_TIME)


class TestNullEnvironmentalValues:
    """Null environmental values must be preserved, never converted to zero."""

    def test_null_values_not_converted_to_zero(self):
        """Environmental reading model allows None for all measurement fields."""
        from app.models.environmental_reading import EnvironmentalReading

        reading = EnvironmentalReading(
            site_id=None,
            timestamp=None,
            temperature=None,
            heat_index=None,
            apparent_temperature=None,
            wet_bulb_temperature=None,
            relative_humidity=None,
            solar_ghi=None,
            solar_dni=None,
            solar_dhi=None,
        )
        # All fields should be None, not zero
        assert reading.temperature is None
        assert reading.heat_index is None
        assert reading.apparent_temperature is None
        assert reading.wet_bulb_temperature is None
        assert reading.relative_humidity is None
        assert reading.solar_ghi is None
        assert reading.solar_dni is None
        assert reading.solar_dhi is None

    def test_actual_values_preserved(self):
        from app.models.environmental_reading import EnvironmentalReading

        reading = EnvironmentalReading(
            temperature=32.5,
            heat_index=38.5,
            relative_humidity=65.0,
            solar_ghi=0.0,  # Zero is a valid measurement, not null
        )
        assert reading.temperature == 32.5
        assert reading.heat_index == 38.5
        assert reading.relative_humidity == 65.0
        assert reading.solar_ghi == 0.0  # Zero is valid, distinct from None
