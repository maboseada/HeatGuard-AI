import asyncio
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.assessment_record import AssessmentRecord
from app.schemas.assessment import (
    AssessmentRequest,
    AssessmentMode,
    AssessmentStatus,
    DataProvenance,
)
from app.services.fortyguard.client import FortyGuardClient
from app.services.fortyguard.heatmap import HeatmapService
from app.services.fortyguard.environmental import EnvironmentalService
from app.services.fortyguard.status import StatusService
from app.services.fortyguard.transformer import FortyGuardTransformer
from app.services.demo.synthetic_fixtures import (
    SYNTHETIC_DUBAI_INDUSTRIAL_HEATMAP,
    SYNTHETIC_DUBAI_INDUSTRIAL_ENV,
)
from app.db.repositories import assessment_repo, site_repo
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AssessmentManager:
    """Orchestrates comprehensive site thermal and environmental assessments."""

    async def run_assessment(
        self,
        db: AsyncSession,
        site_id: UUID,
        request: AssessmentRequest,
        fg_client: FortyGuardClient
    ) -> AssessmentRecord:
        site = await site_repo.get_site(db, site_id)
        if not site:
            raise ValueError(f"Site with id {site_id} not found")

        record = await assessment_repo.create_assessment(db, site_id, request.mode)

        if request.mode == AssessmentMode.DEMO:
            # Handle instant synthetic demo execution
            logger.info(f"Executing SYNTHETIC DEMO assessment for site {site_id}")
            map_geojson, stats = FortyGuardTransformer.normalize_heatmap(
                SYNTHETIC_DUBAI_INDUSTRIAL_HEATMAP,
                provenance=DataProvenance.DEMO_SYNTHETIC
            )
            environmental = FortyGuardTransformer.normalize_environmental(
                SYNTHETIC_DUBAI_INDUSTRIAL_ENV,
                provenance=DataProvenance.DEMO_SYNTHETIC
            )

            completed = await assessment_repo.complete_assessment(
                db,
                record.id,
                raw_heatmap_payload=SYNTHETIC_DUBAI_INDUSTRIAL_HEATMAP,
                raw_env_payload=SYNTHETIC_DUBAI_INDUSTRIAL_ENV,
                map_geojson=map_geojson,
                stats=stats.model_dump() if stats else None,
                environmental=environmental.model_dump() if environmental else None
            )
            return completed

        # LIVE MODE: Submit real FortyGuard tasks
        logger.info(f"Submitting LIVE FortyGuard assessment for site {site_id}")
        heatmap_service = HeatmapService(fg_client)
        env_service = EnvironmentalService(fg_client)

        date_time = request.date_time or {
            "start_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "start_time": datetime.now(timezone.utc).strftime("%H:00"),
            "filter_type": 1
        }

        # Derive coordinates from site boundary or default 100m bounding box
        coords = None
        if site.boundary_geojson and isinstance(site.boundary_geojson, dict):
            coords = site.boundary_geojson.get("coordinates")
        
        if not coords:
            # Fallback 100m square around point
            delta = 0.001
            coords = [[
                [site.longitude - delta, site.latitude - delta],
                [site.longitude + delta, site.latitude - delta],
                [site.longitude + delta, site.latitude + delta],
                [site.longitude - delta, site.latitude + delta],
                [site.longitude - delta, site.latitude - delta],
            ]]

        heatmap_act_id = None
        env_act_id = None

        try:
            heatmap_act_id = await heatmap_service.submit(
                polygon_coordinates=coords,
                date_time=date_time,
                granularity=request.granularity,
                analytic_type=request.analytic_type,
                threshold=request.threshold,
                direction=request.direction
            )
        except Exception as e:
            logger.error(f"Live heatmap submission failed: {e}")

        try:
            env_act_id = await env_service.submit(
                latitude=site.latitude,
                longitude=site.longitude,
                temperature=request.temperature or 35.0,
                date_time=date_time
            )
        except Exception as e:
            logger.error(f"Live environmental submission failed: {e}")

        if not heatmap_act_id and not env_act_id:
            return await assessment_repo.fail_assessment(
                db, record.id, "Failed to initiate any FortyGuard analysis activities."
            )

        updated_record = await assessment_repo.update_assessment_activities(
            db, record.id, heatmap_act_id, env_act_id, AssessmentStatus.PROCESSING
        )

        # Launch background polling task
        asyncio.create_task(
            self._poll_live_assessment(
                record.id,
                heatmap_act_id,
                env_act_id,
                fg_client
            )
        )

        return updated_record

    async def _poll_live_assessment(
        self,
        assessment_id: UUID,
        heatmap_act_id: Optional[str],
        env_act_id: Optional[str],
        fg_client: FortyGuardClient
    ):
        status_service = StatusService(fg_client)
        attempts = 0

        raw_hm_result = None
        raw_env_result = None
        hm_done = heatmap_act_id is None
        env_done = env_act_id is None

        while attempts < settings.MAX_POLL_ATTEMPTS:
            await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)
            attempts += 1

            # Poll heatmap if active
            if not hm_done and heatmap_act_id:
                try:
                    status, res = await status_service.check(heatmap_act_id)
                    if status.lower() == "completed":
                        raw_hm_result = {"data": {"result": res, "status": "Completed"}}
                        hm_done = True
                    elif status.lower() == "failed":
                        hm_done = True
                except Exception as e:
                    logger.warning(f"Heatmap poll error for {assessment_id}: {e}")

            # Poll environmental if active
            if not env_done and env_act_id:
                try:
                    status, res = await status_service.check(env_act_id)
                    if status.lower() == "completed":
                        raw_env_result = {"data": {"result": res, "status": "Completed"}}
                        env_done = True
                    elif status.lower() == "failed":
                        env_done = True
                except Exception as e:
                    logger.warning(f"Environmental poll error for {assessment_id}: {e}")

            if hm_done and env_done:
                break

        # Process and save results
        async with AsyncSessionLocal() as db:
            if not raw_hm_result and not raw_env_result:
                await assessment_repo.fail_assessment(
                    db, assessment_id, "Assessment polling timed out or all jobs failed."
                )
                return

            map_geojson, stats = FortyGuardTransformer.normalize_heatmap(
                raw_hm_result,
                provenance=DataProvenance.RAW_FORTYGUARD
            )
            environmental = FortyGuardTransformer.normalize_environmental(
                raw_env_result,
                provenance=DataProvenance.RAW_FORTYGUARD
            )

            await assessment_repo.complete_assessment(
                db,
                assessment_id,
                raw_heatmap_payload=raw_hm_result,
                raw_env_payload=raw_env_result,
                map_geojson=map_geojson,
                stats=stats.model_dump() if stats else None,
                environmental=environmental.model_dump() if environmental else None
            )
            logger.info(f"Live assessment {assessment_id} successfully completed and normalized.")
