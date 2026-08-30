from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.analysis_job import AnalysisJob

async def create_job(db: AsyncSession, site_id: UUID, analysis_type: str, request_payload: Dict[str, Any]) -> AnalysisJob:
    job = AnalysisJob(
        site_id=site_id,
        analysis_type=analysis_type,
        request_payload=request_payload
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def get_job(db: AsyncSession, job_id: UUID) -> Optional[AnalysisJob]:
    result = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
    return result.scalars().first()

async def update_job_status(db: AsyncSession, job_id: UUID, status: str, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> AnalysisJob:
    job = await get_job(db, job_id)
    if job:
        job.status = status
        if result is not None:
            job.result_payload = result
        if error is not None:
            job.error_message = error
        if status in ["Completed", "Failed"]:
            job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(job)
    return job

async def update_job_activity_id(db: AsyncSession, job_id: UUID, activity_id: str) -> AnalysisJob:
    job = await get_job(db, job_id)
    if job:
        job.activity_id = activity_id
        if job.status == "Pending":
            job.status = "Processing"
        await db.commit()
        await db.refresh(job)
    return job
