import pytest
import sys
from pathlib import Path
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config.database.settings_db import settings_db

sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture
async def test_db_session():
    # Используем базу данных в памяти для тестов
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    session = async_session()
    yield session
    await session.close()
    await test_engine.dispose()

@pytest.fixture
def mock_user_data():
    return {
        "results": [
            {
                "gender": "male",
                "name": {"title": "Mr", "first": "John", "last": "Doe"},
                "location": {
                    "street": {"number": 123, "name": "Main St"},
                    "city": "Anytown",
                    "state": "State",
                    "country": "Country"
                },
                "email": "john.doe@example.com",
                "login": {"uuid": "123e4567-e89b-12d3-a456-426614174000"},
                "dob": {"date": "1990-01-01T00:00:00.000Z", "age": 30},
                "registered": {"date": "2020-01-01T00:00:00.000Z", "age": 3},
                "phone": "555-1234",
                "cell": "555-5678",
                "id": {"name": "SSN", "value": "123-45-6789"},
                "picture": {
                    "large": "http://example.com/large.jpg",
                    "medium": "http://example.com/medium.jpg",
                    "thumbnail": "http://example.com/thumb.jpg"
                },
                "nat": "US"
            }
        ]
    }