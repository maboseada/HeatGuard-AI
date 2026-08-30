import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    boundary_geojson = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
