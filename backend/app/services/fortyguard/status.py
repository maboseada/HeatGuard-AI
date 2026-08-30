from typing import Dict, Any, Tuple, Optional
from app.services.fortyguard.client import FortyGuardClient, FortyGuardAPIError

class StatusService:
    def __init__(self, client: FortyGuardClient):
        self.client = client

    async def check(self, activity_id: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        response = await self.client.get(f"/status/{activity_id}")
        
        if response.get("error"):
            raise FortyGuardAPIError(response.get("message", "Unknown error"))
            
        data = response.get("data", {})
        status = data.get("status")
        result = data.get("result")
        
        if not status:
            raise FortyGuardAPIError("No status returned in response")
            
        return status, result
