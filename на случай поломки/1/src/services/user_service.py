from typing import List, Optional
from sqlmodel import select
from sqlalchemy.sql import func
from sqlmodel.ext.asyncio.session import AsyncSession
from .api_client import RandomUserClient
from src.models.user import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.api_client = RandomUserClient()

    async def _user_exists(self, email: str) -> bool:
        result = await self.session.execute(select(User).where(User.email == email))
        return bool(result.scalars().first())

    async def load_users_from_api(self, count: int) -> int:
        data = await self.api_client.get_users(count)
        
        if not data:
            print("❌ API вернул пустой ответ")
            return 0
        
        if not data.get("results"):
            print("❌ В данных нет ключа 'results'")
            return 0

        print(f"✅ Получено {len(data['results'])} пользователей из API")
                
        loaded = 0
        for result in data["results"]:
            user_data = {
            "gender": result["gender"],
            "first_name": result["name"]["first"],   
            "last_name": result["name"]["last"],   
            "email": result["email"],
            "phone": result["phone"],
            "location": f"{result['location']['city']}, {result['location']['country']}",
            "picture_thumbnail": result["picture"]["thumbnail"]  # если в модели это поле называется так же
        }
            if not await self._user_exists(user_data["email"]):
                user = User(**user_data)
                self.session.add(user)
                loaded += 1
        await self.session.commit()
        return loaded

    async def get_users_paginated(self, page: int = 1, per_page: int = 20) -> dict:
        offset = (page - 1) * per_page
        query = select(User).offset(offset).limit(per_page)
        count_query = select(func.count()).select_from(User)
        
        total = (await self.session.execute(count_query)).scalar_one()
        result = await self.session.execute(query)
        users = result.scalars().all()
        
        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "users": users
        }

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_random_user(self) -> Optional[User]:
        result = await self.session.execute(select(User).order_by(func.random()))
        return result.scalars().first()