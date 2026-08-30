import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base


class AssessmentRecord(Base):
    __tablename__ = "assessment_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    mode = Column(String, default="DEMO")  # "LIVE" or "DEMO"
    status = Column(String, default="Pending")  # Pending, Processing, Completed, Failed
    
    heatmap_activity_id = Column(String, nullable=True)
    env_activity_id = Column(String, nullable=True)
    
    # Preserved unmutated raw payloads
    raw_heatmap_payload = Column(JSON, nullable=True)
    raw_env_payload = Column(JSON, nullable=True)
    
    # Normalized parsed outputs
    map_geojson = Column(JSON, nullable=True)
    stats = Column(JSON, nullable=True)
    environmental = Column(JSON, nullable=True)
    
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    site = relationship("Site")
