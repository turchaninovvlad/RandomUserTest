from typing import List, Optional
from sqlmodel import select
from sqlalchemy.sql import func
from sqlmodel.ext.asyncio.session import AsyncSession
from .api_client import RandomUserClient
from src.models.user import User, UserCreate, UserDetailResponse
import logging


logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.api_client = RandomUserClient()

    async def _user_exists(self, email: str) -> bool:
        result = await self.session.execute(select(User).where(User.email == email))
        return bool(result.scalars().first())

    async def load_users_from_api(self, count: int) -> int:
        data = await self.api_client.get_users(count)
        if not data or "results" not in data:
            return 0

        loaded = 0
        seen_emails = set()  # Добавим множество для защиты от дубликатов

        for result in data["results"]:
            raw_email = result.get("email")
            if isinstance(raw_email, dict):
                email = raw_email.get("value") or raw_email.get("email") or ""
            else:
                email = raw_email or ""

            if not email or email in seen_emails:
                continue

            if not await self._user_exists(email):
                user_data = {
                    "gender": result.get("gender") or "",
                    "name": result.get("name") or {},
                    "location": result.get("location") or {},
                    "email": email,
                    "login": result.get("login") or {},
                    "dob": result.get("dob") or {},
                    "registered": result.get("registered") or {},
                    "phone": result.get("phone") or "",
                    "cell": result.get("cell") or "",
                    "external_id": result.get("id") or {},  # ← Теперь это внешний ID
                    "picture": result.get("picture") or {},
                    "nat": result.get("nat") or ""
                }
                try:
                    user = User(**user_data)
                    self.session.add(user)
                    loaded += 1
                    seen_emails.add(email)
                except Exception as e:
                    logger.error(f"Error creating user: {e}")
                    raise  # Для отладки
                continue

        await self.session.commit() 
        return loaded

    async def get_users_paginated(self, page: int = 1, per_page: int = 20) -> dict:
        offset = (page - 1) * per_page
        query = select(User).offset(offset).limit(per_page)
        count_query = select(func.count()).select_from(User)
        
        total = (await self.session.execute(count_query)).scalar_one()
        result = await self.session.execute(query)
        users = result.scalars().all()
        
        # Форматируем для главной страницы
        formatted_users = []
        for user in users:
            formatted_users.append({
                "id": user.id,
                "gender": user.gender,
                "first_name": user.name["first"],
                "last_name": user.name["last"],
                "email": user.email,
                "phone": user.phone,
                "location": f"{user.location['city']}, {user.location['country']}",
                "picture_thumbnail": user.picture["thumbnail"]
            })
        
        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "users": formatted_users
        }

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_random_user(self) -> Optional[User]:
        result = await self.session.execute(select(User).order_by(func.random()))
        return result.scalars().first()