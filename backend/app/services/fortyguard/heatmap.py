from typing import Dict, Any, List, Optional
import logging
from app.services.fortyguard.client import FortyGuardClient, FortyGuardAPIError

logger = logging.getLogger(__name__)


class HeatmapService:
    def __init__(self, client: FortyGuardClient):
        self.client = client

    async def submit(
        self,
        polygon_coordinates: List[List[List[float]]],
        date_time: Dict[str, Any],
        granularity: int,
        analytic_type: Optional[str] = None,
        threshold: Optional[float] = None,
        direction: Optional[str] = None,
    ) -> str:
        """Submit a heatmap analysis to FortyGuard.

        Args:
            polygon_coordinates: Polygon rings as [[[lng, lat], ...]].
            date_time: Date/time filter dict with start_date, start_time, filter_type.
            granularity: Grid resolution — must be 60, 80, or 100.
            analytic_type: Optional analysis type (tcm, time_of_measure, exceedance, persistence).
            threshold: Optional threshold value for exceedance analysis.
            direction: Optional threshold direction.

        Returns:
            The FortyGuard activity_id for polling.
        """
        if granularity not in (60, 80, 100):
            raise ValueError("Granularity must be 60, 80, or 100")

        # Build the polygon_aoi FeatureCollection matching FortyGuard API spec
        payload: Dict[str, Any] = {
            "polygon_aoi": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": polygon_coordinates,
                        },
                    }
                ],
            },
            "date_time": date_time,
            "granularity": granularity,
        }

        if analytic_type:
            payload["analytic_type"] = analytic_type
        if threshold is not None:
            payload["threshold"] = threshold
        if direction:
            payload["direction"] = direction

        logger.info("Submitting heatmap analysis to FortyGuard")
        response = await self.client.post("/heatmap", json=payload)

        if response.get("error"):
            raise FortyGuardAPIError(response.get("message", "Unknown error"))

        data = response.get("data", {})
        activity_id = data.get("activity_id")

        if not activity_id:
            raise FortyGuardAPIError("No activity_id returned in response")

        logger.info(f"Heatmap submitted successfully, activity_id={activity_id}")
        return activity_id
