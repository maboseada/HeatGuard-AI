import httpx
import logging
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)

class FortyGuardAPIError(Exception):
    pass

class FortyGuardTimeoutError(Exception):
    pass

class FortyGuardClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"api-key": self.api_key},
            timeout=self.timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            
    async def post(self, endpoint: str, json: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"POST {endpoint}")
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers={"api-key": self.api_key},
                timeout=self.timeout
            ) as client:
                response = await client.post(endpoint, json=json)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            logger.error(f"Timeout on POST {endpoint}")
            raise FortyGuardTimeoutError(f"Timeout: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error on POST {endpoint}: {e.response.text}")
            raise FortyGuardAPIError(f"HTTP Error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error on POST {endpoint}: {str(e)}")
            raise FortyGuardAPIError(f"Error: {str(e)}")

    async def get(self, endpoint: str) -> Dict[str, Any]:
        try:
            logger.info(f"GET {endpoint}")
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers={"api-key": self.api_key},
                timeout=self.timeout
            ) as client:
                response = await client.get(endpoint)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            logger.error(f"Timeout on GET {endpoint}")
            raise FortyGuardTimeoutError(f"Timeout: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error on GET {endpoint}: {e.response.text}")
            raise FortyGuardAPIError(f"HTTP Error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error on GET {endpoint}: {str(e)}")
            raise FortyGuardAPIError(f"Error: {str(e)}")
