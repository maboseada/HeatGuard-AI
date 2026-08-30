import uuid
from sqlalchemy import Column, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class EnvironmentalReading(Base):
    __tablename__ = "environmental_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    timestamp = Column(DateTime, nullable=False)
    
    # Nullable values, null means unavailable, NEVER zero
    temperature = Column(Float, nullable=True)
    heat_index = Column(Float, nullable=True)
    apparent_temperature = Column(Float, nullable=True)
    wet_bulb_temperature = Column(Float, nullable=True)
    relative_humidity = Column(Float, nullable=True)
    solar_ghi = Column(Float, nullable=True)
    solar_dni = Column(Float, nullable=True)
    solar_dhi = Column(Float, nullable=True)

    site = relationship("Site")
