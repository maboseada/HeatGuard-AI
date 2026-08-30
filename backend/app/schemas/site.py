from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID

class SiteCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    boundary_geojson: Optional[Dict[str, Any]] = None

class SiteResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    latitude: float
    longitude: float
    boundary_geojson: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
