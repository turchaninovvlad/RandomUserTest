import httpx
from typing import Any

class RandomUserAPI:
    def __init__(self):
        self.base_url = "https://randomuser.me/api/"

    async def fetch_users(self, results: int = 100):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url,
                params={
                    "results": results,
                    "inc": "gender,name,email,phone,location,picture",
                    "noinfo": True
                }
            )
            response.raise_for_status()
            return self._parse_response(response.json())

    def _parse_response(self, data: dict) -> list[dict[str, Any]]:
        return [
            {
                "gender": user["gender"],
                "firstName": user["name"]["first"],
                "lastName": user["name"]["last"],
                "email": user["email"],
                "phone": user["phone"],
                "street": f"{user['location']['street']['number']} {user['location']['street']['name']}",
                "city": user["location"]["city"],
                "state": user["location"]["state"],
                "country": user["location"]["country"],
                "pictureSmall": user["picture"]["thumbnail"],
                "pictureLarge": user["picture"]["large"]
            }
            for user in data["results"]
        ]