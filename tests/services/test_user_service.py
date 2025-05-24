import pytest
from unittest.mock import AsyncMock
from sqlmodel.ext.asyncio.session import AsyncSession
from src.services.user_service import UserService
from src.models.user import User
from sqlalchemy import text

@pytest.mark.asyncio
async def test_load_users_from_api(test_db_session: AsyncSession, mocker):
    mock_data = {
        "results": [
            {
                "gender": "male",
                "name": {"title": "Mr", "first": "John", "last": "Doe"},
                "email": "john.doe@example.com",
                "login": {"uuid": "123"},
                "location": {
                    "city": "New York",
                    "country": "USA",
                    "street": {"number": 123, "name": "Main St"},
                    "state": "NY"
                },
                "dob": {"date": "1990-01-01", "age": 30},
                "registered": {"date": "2020-01-01"},
                "phone": "123-456",
                "cell": "789-012",
                "id": {"value": "123"},
                "picture": {"thumbnail": "test.jpg"},
                "nat": "US"
            }
        ]
    }
    mocker.patch(
        "src.services.user_service.RandomUserClient.get_users",
        return_value=mock_data
    )

    service = UserService(test_db_session)
    loaded = await service.load_users_from_api(1)
    
    assert loaded == 1
    result = await test_db_session.execute(text("SELECT COUNT(*) FROM user"))
    count = result.scalar_one()
    assert count == 1

@pytest.mark.asyncio
async def test_get_users_paginated(test_db_session: AsyncSession):
    users = [
        User(
            gender="male",
            name={"first": "John", "last": "Doe"},
            email=f"user{i}@test.com",
            phone="123-456",
            location={
                "city": "City",
                "country": "Country",
                "street": {"number": 123, "name": "Street"},
                "state": "State"
            },
            login={},
            dob={},
            registered={},
            cell="",
            picture={"thumbnail": "test.jpg"},
            nat="US"
        )
        for i in range(1, 6)
    ]
    for user in users:
        test_db_session.add(user)
    await test_db_session.commit()

    service = UserService(test_db_session)
    result = await service.get_users_paginated(page=1, per_page=3)
    
    assert result["total"] == 5
    assert len(result["users"]) == 3
    assert result["users"][0]["location"] == "City, Country"

@pytest.mark.asyncio
async def test_get_user_by_id(test_db_session: AsyncSession):
    user = User(
        gender="female",
        name={"first": "Jane", "last": "Doe"},
        email="jane@test.com",
        phone="555-1234",
        location={},
        login={},
        dob={},
        registered={},
        cell="",
        picture={},
        nat="US"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    service = UserService(test_db_session)
    found = await service.get_user_by_id(user.id)
    
    assert found is not None
    assert found.email == "jane@test.com"

@pytest.mark.asyncio
async def test_get_random_user(test_db_session: AsyncSession):
    # Добавляем несколько пользователей
    for i in range(3):
        user = User(
            gender="male",
            name={"first": f"User{i}", "last": "Test"},
            email=f"user{i}@test.com",
            phone="123-456",
            location={},
            login={},
            dob={},
            registered={},
            cell="",
            picture={},
            nat="US"
        )
        test_db_session.add(user)
    await test_db_session.commit()

    service = UserService(test_db_session)
    random_user = await service.get_random_user()
    
    assert random_user is not None
    assert "user" in random_user.email