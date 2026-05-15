import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_redis():
    return MagicMock()


@pytest.fixture
def iam_client(mock_redis):
    mock_http = AsyncMock()
    with patch("iam_client.client.redis") as mock_redis_module, \
         patch("iam_client.client.httpx") as mock_httpx:
        mock_redis_module.from_url.return_value = mock_redis
        mock_httpx.AsyncClient.return_value = mock_http
        from iam_client.client import AsyncIAMClient
        client = AsyncIAMClient(base_url="http://test-iam", redis_url="redis://localhost")
        client.redis = mock_redis
        client.http = mock_http
        yield client, mock_redis, mock_http
