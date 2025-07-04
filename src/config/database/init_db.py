from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from .db_helper import engine, async_session_maker

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

