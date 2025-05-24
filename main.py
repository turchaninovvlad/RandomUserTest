from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from src.routes.users import router as users_router
from src.config.database.init_db import init_db
from src.config.database.db_helper import get_session
from src.services.user_service import UserService
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация БД
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    


    try:
        async for session in get_session():
            try:
                service = UserService(session)
                loaded_count = await service.load_users_from_api(1000)
                #logger.info(f"Successfully loaded {loaded_count} users on startup")
                if loaded_count == 0:
                    logger.warning("No users were loaded - API might be unavailable")
            except Exception as e:
                logger.error(f"Error loading users: {str(e)}")
            finally:
                await session.close()
    except Exception as e:
            logger.error(f"Database session error: {str(e)}")
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

