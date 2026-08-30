import asyncio
import logging
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.analysis_job import AnalysisJob
from app.schemas.job import HeatmapRequest, EnvironmentalRequest, JobStatus, AnalysisType
from app.schemas.site import SiteResponse
from app.services.fortyguard.client import FortyGuardClient
from app.services.fortyguard.heatmap import HeatmapService
from app.services.fortyguard.environmental import EnvironmentalService
from app.services.fortyguard.status import StatusService
from app.db.repositories import job_repo, site_repo
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class JobManager:
    async def submit_heatmap(self, db: AsyncSession, site_id: UUID, request: HeatmapRequest, fg_client: FortyGuardClient) -> AnalysisJob:
        job = await job_repo.create_job(
            db, 
            site_id=site_id, 
            analysis_type=AnalysisType.heatmap.value,
            request_payload=request.model_dump()
        )
        
        heatmap_service = HeatmapService(fg_client)
        try:
            activity_id = await heatmap_service.submit(
                polygon_coordinates=request.polygon_coordinates,
                date_time=request.date_time.model_dump(),
                granularity=request.granularity,
                analytic_type=request.analytic_type,
                threshold=request.threshold,
                direction=request.direction
            )
            job = await job_repo.update_job_activity_id(db, job.id, activity_id)
            asyncio.create_task(self._poll_status(job.id, activity_id, fg_client))
        except Exception as e:
            logger.error(f"Failed to submit heatmap job: {e}")
            job = await job_repo.update_job_status(db, job.id, JobStatus.failed.value, error=str(e))
            
        return job

    async def submit_environmental(self, db: AsyncSession, site_id: UUID, request: EnvironmentalRequest, fg_client: FortyGuardClient) -> AnalysisJob:
        job = await job_repo.create_job(
            db, 
            site_id=site_id, 
            analysis_type=AnalysisType.environmental.value,
            request_payload=request.model_dump()
        )
        
        site = await site_repo.get_site(db, site_id)
        if not site:
            job = await job_repo.update_job_status(db, job.id, JobStatus.failed.value, error="Site not found")
            return job

        env_service = EnvironmentalService(fg_client)
        try:
            activity_id = await env_service.submit(
                latitude=site.latitude,
                longitude=site.longitude,
                temperature=request.temperature,
                date_time=request.date_time.model_dump()
            )
            job = await job_repo.update_job_activity_id(db, job.id, activity_id)
            asyncio.create_task(self._poll_status(job.id, activity_id, fg_client))
        except Exception as e:
            logger.error(f"Failed to submit environmental job: {e}")
            job = await job_repo.update_job_status(db, job.id, JobStatus.failed.value, error=str(e))
            
        return job

    async def _poll_status(self, job_id: UUID, activity_id: str, fg_client: FortyGuardClient):
        status_service = StatusService(fg_client)
        attempts = 0
        
        while attempts < settings.MAX_POLL_ATTEMPTS:
            await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)
            attempts += 1
            
            async with AsyncSessionLocal() as db:
                try:
                    status, result = await status_service.check(activity_id)
                    logger.info(f"Polled job {job_id} (Activity: {activity_id}): {status}")
                    
                    if status.lower() == "completed":
                        await job_repo.update_job_status(db, job_id, JobStatus.completed.value, result=result)
                        return
                    elif status.lower() == "failed":
                        await job_repo.update_job_status(db, job_id, JobStatus.failed.value, error="FortyGuard job failed")
                        return
                        
                except Exception as e:
                    logger.error(f"Error polling job {job_id}: {e}")
                    # Allow transient errors, keep polling
                    
        # Timeout
        async with AsyncSessionLocal() as db:
            await job_repo.update_job_status(db, job_id, JobStatus.failed.value, error="Polling timeout")
