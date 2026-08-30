from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.database import get_db
from app.schemas.assessment import AssessmentRequest, AssessmentResponse
from app.services.jobs.assessment_manager import AssessmentManager
from app.services.fortyguard.client import FortyGuardClient
from app.api.dependencies import get_assessment_manager, get_fortyguard_client
from app.db.repositories import assessment_repo

router = APIRouter()


@router.post("/{site_id}/assess", response_model=AssessmentResponse)
async def run_site_assessment(
    site_id: UUID,
    request: AssessmentRequest,
    db: AsyncSession = Depends(get_db),
    manager: AssessmentManager = Depends(get_assessment_manager),
    fg_client: FortyGuardClient = Depends(get_fortyguard_client)
):
    try:
        record = await manager.run_assessment(db, site_id, request, fg_client)
        return record
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")


@router.get("/{site_id}/assessment/latest", response_model=AssessmentResponse)
async def get_latest_site_assessment(
    site_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    record = await assessment_repo.get_latest_site_assessment(db, site_id)
    if not record:
        raise HTTPException(status_code=404, detail="No assessment found for this site.")
    return record


@router.get("/assessments/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment_by_id(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    record = await assessment_repo.get_assessment(db, assessment_id)
    if not record:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return record
