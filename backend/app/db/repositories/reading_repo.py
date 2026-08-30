from typing import List
from uuid import UUID
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.environmental_reading import EnvironmentalReading

async def create_reading(db: AsyncSession, site_id: UUID, timestamp: datetime.datetime, **kwargs) -> EnvironmentalReading:
    reading = EnvironmentalReading(
        site_id=site_id,
        timestamp=timestamp,
        **kwargs
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading

async def get_readings_for_site(db: AsyncSession, site_id: UUID) -> List[EnvironmentalReading]:
    result = await db.execute(select(EnvironmentalReading).where(EnvironmentalReading.site_id == site_id))
    return list(result.scalars().all())
