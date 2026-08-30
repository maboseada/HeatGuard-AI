from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.database import get_db
from app.schemas.job import HeatmapRequest, EnvironmentalRequest, JobSubmissionResponse, JobStatus
from app.services.jobs.manager import JobManager
from app.services.fortyguard.client import FortyGuardClient
from app.api.dependencies import get_job_manager, get_fortyguard_client

router = APIRouter()

@router.post("/{site_id}/heatmap", response_model=JobSubmissionResponse)
async def submit_heatmap(
    site_id: UUID, 
    request: HeatmapRequest, 
    db: AsyncSession = Depends(get_db),
    job_manager: JobManager = Depends(get_job_manager),
    fg_client: FortyGuardClient = Depends(get_fortyguard_client)
):
    job = await job_manager.submit_heatmap(db, site_id, request, fg_client)
    return JobSubmissionResponse(
        job_id=job.id,
        activity_id=job.activity_id,
        status=JobStatus(job.status) if job.status else JobStatus.pending
    )

@router.post("/{site_id}/environment", response_model=JobSubmissionResponse)
async def submit_environment(
    site_id: UUID, 
    request: EnvironmentalRequest, 
    db: AsyncSession = Depends(get_db),
    job_manager: JobManager = Depends(get_job_manager),
    fg_client: FortyGuardClient = Depends(get_fortyguard_client)
):
    job = await job_manager.submit_environmental(db, site_id, request, fg_client)
    return JobSubmissionResponse(
        job_id=job.id,
        activity_id=job.activity_id,
        status=JobStatus(job.status) if job.status else JobStatus.pending
    )
