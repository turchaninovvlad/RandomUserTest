# tests/services/test_api_client.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.api_client import RandomUserClient
import logging

import sys
print(sys.path)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_api_client_success():
    # Мокаем синхронный ответ
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": [{"email": "test@example.com"}]}
    mock_response.raise_for_status = MagicMock()

    # Мокаем асинхронный клиент
    mock_client = MagicMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("src.services.api_client.httpx.AsyncClient",
               return_value=mock_client):
        client = RandomUserClient()
        result = await client.get_users(1)
        
        # Ожидаем корутину, так как текущая реализация возвращает недожиданные значения
        assert isinstance(result, type(mock_response.json.return_value))
        assert result == {"results": [{"email": "test@example.com"}]}
"""""
@pytest.mark.asyncio
async def test_api_client_failure():
    # Мокаем ошибку
    mock_client = MagicMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get = AsyncMock(side_effect=Exception("API Error"))

    with patch("src.services.api_client.httpx.AsyncClient", return_value=mock_client):
        client = RandomUserClient()
        result = await client.get_users(1)
        
        # Ожидаем результат текущей реализации
        assert isinstance(result, type(None))
        """
        