from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.database import get_db
from app.schemas.job import JobResponse
from app.db.repositories import job_repo

router = APIRouter()

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    job = await job_repo.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
