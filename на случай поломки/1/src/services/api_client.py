import httpx
from typing import Optional

class RandomUserClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url="https://randomuser.me/api/")

    async def get_users(self, count: int = 1) -> Optional[dict]:
        try:
            response = await self.client.get("", params={"results": count})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"API Error: {e}")
            return None

    async def close(self):
        await self.client.aclose()