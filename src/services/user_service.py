from typing import List, Optional
from sqlmodel import select
from sqlalchemy.sql import func
from sqlmodel.ext.asyncio.session import AsyncSession
from .api_client import RandomUserClient
from src.models.user import User, UserCreate, UserDetailResponse
import logging


from typing import Dict, Any


logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.api_client = RandomUserClient()

    async def _get_existing_emails(self, emails: list[str]) -> set[str]:
        if not emails:
            return set()
        
        # Разбиваем на чанки для SQLite (лимит 999 параметров)
        chunk_size = 999
        existing_emails = set()
        
        for i in range(0, len(emails), chunk_size):
            chunk = emails[i:i + chunk_size]
            result = await self.session.execute(
                select(User.email).where(User.email.in_(chunk))
            )
            existing_emails.update({email for email in result.scalars()})
            
        return existing_emails

    async def load_users_from_api(self, count: int) -> int:
        data = await self.api_client.get_users(count)
        if not data or "results" not in data:
            return 0

        # Сбор и обработка email
        email_mapping: Dict[str, Dict[str, Any]] = {}
        for result in data["results"]:
            raw_email = result.get("email")
            email = self._parse_email(raw_email)
            
            if email and email not in email_mapping:
                email_mapping[email] = result

        # Проверка существующих email
        existing_emails = await self._get_existing_emails(list(email_mapping.keys()))
        
        # Подготовка данных для вставки
        users_to_add = []
        for email, result in email_mapping.items():
            if email in existing_emails:
                continue
            
            try:
                user = self._create_user_from_result(result, email)
                users_to_add.append(user)
            except Exception as e:
                logger.error(f"Error creating user {email}: {e}")

        # Bulk insert
        if users_to_add:
            self.session.add_all(users_to_add)
            try:
                await self.session.commit()
            except Exception as e:
                logger.error(f"Commit error: {e}")
                await self.session.rollback()
                return 0
                
        return len(users_to_add)

    def _parse_email(self, raw_email: Any) -> str:
        if isinstance(raw_email, dict):
            return raw_email.get("value") or raw_email.get("email") or ""
        return str(raw_email or "")

    def _create_user_from_result(self, result: dict, email: str) -> User:
        return User(
            gender=result.get("gender") or "",
            name=result.get("name") or {},
            location=result.get("location") or {},
            email=email,
            login=result.get("login") or {},
            dob=result.get("dob") or {},
            registered=result.get("registered") or {},
            phone=result.get("phone") or "",
            cell=result.get("cell") or "",
            external_id=result.get("id") or {},
            picture=result.get("picture") or {},
            nat=result.get("nat") or ""
        )

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