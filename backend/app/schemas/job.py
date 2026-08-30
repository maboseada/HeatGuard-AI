from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from uuid import UUID
from .common import JobStatus, AnalysisType

class DateTimeFilter(BaseModel):
    start_date: str
    start_time: str
    filter_type: int

class HeatmapRequest(BaseModel):
    polygon_coordinates: List[List[List[float]]]
    date_time: DateTimeFilter
    granularity: int = Field(..., description="60, 80, or 100")
    analytic_type: Optional[str] = None
    threshold: Optional[float] = None
    direction: Optional[str] = None

class EnvironmentalRequest(BaseModel):
    temperature: float
    date_time: DateTimeFilter

class JobResponse(BaseModel):
    id: UUID
    site_id: UUID
    provider: str
    activity_id: Optional[str]
    analysis_type: AnalysisType
    status: JobStatus
    request_payload: Dict[str, Any]
    result_payload: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}

class JobSubmissionResponse(BaseModel):
    job_id: UUID
    activity_id: Optional[str]
    status: JobStatus
