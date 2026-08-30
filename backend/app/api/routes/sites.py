from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.db.database import get_db
from app.schemas.site import SiteCreate, SiteResponse
from app.db.repositories import site_repo

router = APIRouter()

@router.post("", response_model=SiteResponse)
async def create_site(site: SiteCreate, db: AsyncSession = Depends(get_db)):
    return await site_repo.create_site(db, site)

@router.get("", response_model=List[SiteResponse])
async def list_sites(db: AsyncSession = Depends(get_db)):
    return await site_repo.list_sites(db)

@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(site_id: UUID, db: AsyncSession = Depends(get_db)):
    site = await site_repo.get_site(db, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site
