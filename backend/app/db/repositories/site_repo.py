from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.site import Site
from app.schemas.site import SiteCreate


async def create_site(db: AsyncSession, site_create: SiteCreate) -> Site:
    site = Site(
        name=site_create.name,
        latitude=site_create.latitude,
        longitude=site_create.longitude,
        description=site_create.description,
        boundary_geojson=site_create.boundary_geojson
    )
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return site


async def get_site(db: AsyncSession, site_id: UUID) -> Optional[Site]:
    result = await db.execute(select(Site).where(Site.id == site_id))
    return result.scalars().first()


async def list_sites(db: AsyncSession) -> List[Site]:
    result = await db.execute(select(Site))
    sites = list(result.scalars().all())
    
    # If DB is empty, auto-seed default demonstration sites
    if not sites:
        site1 = Site(
            name="Dubai Industrial Park (Sector 4 - Fabrication Yard)",
            description="Heavy industrial manufacturing and steel fabrication facility with high solar exposure.",
            latitude=25.2048,
            longitude=55.2708,
            boundary_geojson={
                "type": "Polygon",
                "coordinates": [
                    [
                        [55.2690, 25.2030],
                        [55.2730, 25.2030],
                        [55.2730, 25.2070],
                        [55.2690, 25.2070],
                        [55.2690, 25.2030]
                    ]
                ]
            }
        )
        site2 = Site(
            name="Houston Ship Channel (Petrochemical Terminal B)",
            description="Coastal chemical storage and pipeline transfer terminal with elevated humidity.",
            latitude=29.7350,
            longitude=-95.1200,
            boundary_geojson={
                "type": "Polygon",
                "coordinates": [
                    [
                        [-95.1220, 29.7330],
                        [-95.1180, 29.7330],
                        [-95.1180, 29.7370],
                        [-95.1220, 29.7370],
                        [-95.1220, 29.7330]
                    ]
                ]
            }
        )
        db.add_all([site1, site2])
        await db.commit()
        await db.refresh(site1)
        await db.refresh(site2)
        return [site1, site2]
        
    return sites
