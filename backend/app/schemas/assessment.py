from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class DataProvenance(str, Enum):
    RAW_FORTYGUARD = "raw_fortyguard"      # Directly returned from FortyGuard API
    DERIVED = "derived"                    # Calculated by HeatGuard AI (Phase 3)
    SIMULATED = "simulated"                # Assumption-based What-If output (Phase 3)
    DEMO_SYNTHETIC = "demo_synthetic"      # Explicitly labeled synthetic test fixture


class AssessmentMode(str, Enum):
    LIVE = "LIVE"
    DEMO = "DEMO"


class NormalizedEnvironmental(BaseModel):
    provenance: DataProvenance
    temperature: Optional[float] = None
    heat_index: Optional[float] = None
    apparent_temperature: Optional[float] = None
    wet_bulb_temperature: Optional[float] = None
    relative_humidity: Optional[float] = None
    solar_irradiance: Optional[float] = None
    precipitation_mm: Optional[float] = None
    cloud_cover_octas: Optional[float] = None
    air_quality_index: Optional[float] = None


class NormalizedHeatmapStats(BaseModel):
    provenance: DataProvenance
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    mean_temperature: Optional[float] = None
    median_temperature: Optional[float] = None
    standard_deviation: Optional[float] = None
    granularity: Optional[int] = None


class AssessmentStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"


class AssessmentRequest(BaseModel):
    mode: AssessmentMode = AssessmentMode.DEMO
    date_time: Optional[Dict[str, Any]] = None
    granularity: int = Field(default=100, description="60, 80, or 100")
    temperature: Optional[float] = None
    analytic_type: Optional[str] = "tcm"
    threshold: Optional[float] = None
    direction: Optional[str] = None


class AssessmentResponse(BaseModel):
    id: UUID
    site_id: UUID
    mode: AssessmentMode
    status: AssessmentStatus
    heatmap_activity_id: Optional[str] = None
    env_activity_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    # Preserved raw responses
    raw_heatmap_payload: Optional[Dict[str, Any]] = None
    raw_env_payload: Optional[Dict[str, Any]] = None

    # Normalized internal representations
    map_geojson: Optional[Dict[str, Any]] = None
    stats: Optional[NormalizedHeatmapStats] = None
    environmental: Optional[NormalizedEnvironmental] = None

    model_config = {"from_attributes": True}
