import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime, timezone


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    provider = Column(String, default="fortyguard")
    activity_id = Column(String, nullable=True, unique=True)
    analysis_type = Column(String)  # heatmap or environmental
    status = Column(String, default="Pending")
    request_payload = Column(JSON)
    result_payload = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    site = relationship("Site")

