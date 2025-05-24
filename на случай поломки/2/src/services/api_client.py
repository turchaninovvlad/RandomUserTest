import httpx
from typing import Optional
import logging
from typing import Any

logger = logging.getLogger(__name__)

class RandomUserClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url="https://randomuser.me/api/")

    async def get_users(self, count: int = 1) -> Optional[dict]:
        try:
            response = await self.client.get("", params={"results": count})
            response.raise_for_status()

            data = response.json() 

            
            logger.info("Raw response from API:")
            logger.info(data)

            return data

        except httpx.HTTPError as e:
            logger.error(f"API Error: {e}")
            return None

    async def close(self):
        await self.client.aclose()