from typing import Dict, Any
import logging
from app.services.fortyguard.client import FortyGuardClient, FortyGuardAPIError

logger = logging.getLogger(__name__)


class EnvironmentalService:
    def __init__(self, client: FortyGuardClient):
        self.client = client

    async def submit(
        self,
        latitude: float,
        longitude: float,
        temperature: float,
        date_time: Dict[str, Any],
    ) -> str:
        """Submit an environmental parameters analysis to FortyGuard.

        Args:
            latitude: Site latitude.
            longitude: Site longitude.
            temperature: Current temperature in Celsius.
            date_time: Date/time filter dict with start_date, start_time, filter_type.

        Returns:
            The FortyGuard activity_id for polling.
        """
        # Payload matches FortyGuard /env_params API spec — flat lat/lng at top level
        payload: Dict[str, Any] = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": temperature,
            "date_time": date_time,
        }

        logger.info("Submitting environmental analysis to FortyGuard")
        response = await self.client.post("/env_params", json=payload)

        if response.get("error"):
            raise FortyGuardAPIError(response.get("message", "Unknown error"))

        data = response.get("data", {})
        activity_id = data.get("activity_id")

        if not activity_id:
            raise FortyGuardAPIError("No activity_id returned in response")

        logger.info(f"Environmental analysis submitted, activity_id={activity_id}")
        return activity_id
