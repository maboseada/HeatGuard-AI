from pydantic import BaseModel
from typing import Optional, Dict, Any

class FortyGuardResponse(BaseModel):
    error: bool
    status_code: int
    message: str
    data: Optional[Dict[str, Any]] = None

class FortyGuardStatusData(BaseModel):
    activity_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
