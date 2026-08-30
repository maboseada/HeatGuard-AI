from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.assessment_record import AssessmentRecord
from app.schemas.assessment import AssessmentStatus, AssessmentMode


async def create_assessment(
    db: AsyncSession,
    site_id: UUID,
    mode: AssessmentMode
) -> AssessmentRecord:
    record = AssessmentRecord(
        site_id=site_id,
        mode=mode.value,
        status=AssessmentStatus.PENDING.value
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_assessment(
    db: AsyncSession,
    assessment_id: UUID
) -> Optional[AssessmentRecord]:
    result = await db.execute(select(AssessmentRecord).where(AssessmentRecord.id == assessment_id))
    return result.scalars().first()


async def get_latest_site_assessment(
    db: AsyncSession,
    site_id: UUID
) -> Optional[AssessmentRecord]:
    result = await db.execute(
        select(AssessmentRecord)
        .where(AssessmentRecord.site_id == site_id)
        .order_by(AssessmentRecord.created_at.desc())
    )
    return result.scalars().first()


async def update_assessment_activities(
    db: AsyncSession,
    assessment_id: UUID,
    heatmap_activity_id: Optional[str] = None,
    env_activity_id: Optional[str] = None,
    status: AssessmentStatus = AssessmentStatus.PROCESSING
) -> Optional[AssessmentRecord]:
    record = await get_assessment(db, assessment_id)
    if record:
        if heatmap_activity_id:
            record.heatmap_activity_id = heatmap_activity_id
        if env_activity_id:
            record.env_activity_id = env_activity_id
        record.status = status.value
        await db.commit()
        await db.refresh(record)
    return record


async def complete_assessment(
    db: AsyncSession,
    assessment_id: UUID,
    raw_heatmap_payload: Optional[Dict[str, Any]],
    raw_env_payload: Optional[Dict[str, Any]],
    map_geojson: Optional[Dict[str, Any]],
    stats: Optional[Dict[str, Any]],
    environmental: Optional[Dict[str, Any]]
) -> Optional[AssessmentRecord]:
    record = await get_assessment(db, assessment_id)
    if record:
        record.status = AssessmentStatus.COMPLETED.value
        record.raw_heatmap_payload = raw_heatmap_payload
        record.raw_env_payload = raw_env_payload
        record.map_geojson = map_geojson
        record.stats = stats
        record.environmental = environmental
        record.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(record)
    return record


async def fail_assessment(
    db: AsyncSession,
    assessment_id: UUID,
    error_message: str
) -> Optional[AssessmentRecord]:
    record = await get_assessment(db, assessment_id)
    if record:
        record.status = AssessmentStatus.FAILED.value
        record.error_message = error_message
        record.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(record)
    return record
