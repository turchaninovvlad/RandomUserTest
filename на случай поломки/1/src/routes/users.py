from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
from src.services.user_service import UserService
from src.config.database.db_helper import get_session
from src.models.user import UserResponse, UserRandomResponse

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/")
async def home(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    try:
        data = await service.get_users_paginated(page, per_page)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "users": data["users"],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": data["total"],
                    "total_pages": (data["total"] + per_page - 1) // per_page
                }
            }
        )
    finally:
        await session.close()

@router.post("/load-users")
async def load_users(
    count: int = Form(...),
    session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    try:
        if count < 1 or count > 5000:
            raise HTTPException(400, "Count must be between 1 and 5000")
        
        loaded = await service.load_users_from_api(count)
        return {"message": f"Successfully loaded {loaded} new users"}
    finally:
        await session.close()

@router.get("/user/{user_id}")
async def get_user(
    user_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    try:
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(404)
        
        return templates.TemplateResponse(
            "user_detail.html",
            {
                "request": request,
                "user": {
                    "id": user.id,
                    "gender": user.gender,
                    "full_name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "phone": user.phone,
                    "location": user.location,
                    "picture_large": user.picture_thumbnail.replace("thumbnail", "large")
                }
            }
        )
    finally:
        await session.close()

@router.get("/random")
async def get_random_user(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    try:
        user = await service.get_random_user()
        if not user:
            raise HTTPException(404)
        
        return templates.TemplateResponse(
            "random_user.html",
            {
                "request": request,
                "user": {
                    "id": user.id,
                    "gender": user.gender,
                    "full_name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "phone": user.phone,
                    "location": user.location,
                    "picture_large": user.picture_thumbnail.replace("thumbnail", "large")
                }
            }
        )
    finally:
        await session.close()