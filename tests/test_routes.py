from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, AsyncMock
from src.models.user import User

client = TestClient(app)

def test_home_route():
    mock_data = {
        "total": 0,
        "page": 1,
        "per_page": 20,
        "users": []
    }
    with patch("src.routes.users.UserService") as MockUserService:
        mock_service = MockUserService.return_value
        mock_service.get_users_paginated = AsyncMock(return_value=mock_data)
        
        response = client.get("/")
        assert response.status_code == 200
        # Изменяем проверку на актуальный заголовок из шаблона
        assert "Random Users" in response.text

def test_load_users_route():
    with patch("src.routes.users.UserService") as MockUserService:
        mock_service = MockUserService.return_value
        mock_service.load_users_from_api = AsyncMock(return_value=5)
        
        response = client.post("/load-users", data={"count": 5})
        assert response.status_code == 200
        assert "Successfully loaded 5 new users" in response.text


# tests/test_routes.py
def test_random_user_route():
    mock_user = User(
        id=1,
        gender="male",
        name={"first": "John", "last": "Doe"},
        email="john@example.com",
        phone="123-456",
        location={
            "street": {"number": 123, "name": "Main St"},
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postcode": "10001",
            "coordinates": {"latitude": "40.7128", "longitude": "-74.0060"},
            "timezone": {"offset": "-5:00", "description": "Eastern Time"}
        },
        picture={"large": "test.jpg"}
    )
    with patch("src.routes.users.UserService") as MockUserService:
        mock_service = MockUserService.return_value
        mock_service.get_random_user = AsyncMock(return_value=mock_user)
        
        response = client.get("/random")
        assert response.status_code == 200
        assert "Random User" in response.text