import json
import time
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from jose import jwt


# ---------------------------------------------------------------------------
# decode_local
# ---------------------------------------------------------------------------

def test_decode_local_success(iam_client):
    client, mock_redis, _ = iam_client
    secret = "test-secret"
    payload = {"sub": "user1", "email": "u@t.com", "exp": int(time.time()) + 3600}
    token = jwt.encode(payload, secret, algorithm="HS256")

    result = client.decode_local(token, secret)
    assert result["sub"] == "user1"


def test_decode_local_wrong_secret_raises(iam_client):
    client, _, _ = iam_client
    secret = "test-secret"
    payload = {"sub": "user1", "exp": int(time.time()) + 3600}
    token = jwt.encode(payload, secret, algorithm="HS256")

    with pytest.raises(Exception):
        client.decode_local(token, "wrong-secret")


def test_decode_local_expired_token_raises(iam_client):
    client, _, _ = iam_client
    secret = "test-secret"
    payload = {"sub": "user1", "exp": int(time.time()) - 100}
    token = jwt.encode(payload, secret, algorithm="HS256")

    with pytest.raises(Exception):
        client.decode_local(token, secret)


# ---------------------------------------------------------------------------
# get_cached_user
# ---------------------------------------------------------------------------

def test_get_cached_user_hit(iam_client):
    client, mock_redis, _ = iam_client
    user_data = {
        "user_id": "user1",
        "email": "user1@test.com",
        "roles": ["admin"],
        "permissions": ["read"],
        "valid": True,
    }
    mock_redis.get.return_value = json.dumps(user_data)

    result = client.get_cached_user("test-token")

    assert result is not None
    assert result.user_id == "user1"
    assert result.roles == ["admin"]
    mock_redis.get.assert_called_once_with("iam:test-token")


def test_get_cached_user_miss(iam_client):
    client, mock_redis, _ = iam_client
    mock_redis.get.return_value = None

    result = client.get_cached_user("test-token")

    assert result is None
    mock_redis.get.assert_called_once_with("iam:test-token")


# ---------------------------------------------------------------------------
# set_cache
# ---------------------------------------------------------------------------

def test_set_cache_default_ttl(iam_client):
    client, mock_redis, _ = iam_client
    user_data = {"user_id": "u1", "email": "u@t.com", "roles": [], "permissions": [], "valid": True}

    client.set_cache("tok", user_data)

    mock_redis.setex.assert_called_once_with("iam:tok", 300, json.dumps(user_data))


def test_set_cache_custom_ttl(iam_client):
    client, mock_redis, _ = iam_client
    user_data = {"user_id": "u1", "email": "u@t.com", "roles": [], "permissions": [], "valid": True}

    client.set_cache("tok", user_data, ttl=600)

    mock_redis.setex.assert_called_once_with("iam:tok", 600, json.dumps(user_data))


# ---------------------------------------------------------------------------
# evict_cache
# ---------------------------------------------------------------------------

def test_evict_cache_calls_delete(iam_client):
    client, mock_redis, _ = iam_client

    client.evict_cache("test-token")

    mock_redis.delete.assert_called_once_with("iam:test-token")


def test_evict_cache_swallows_exception(iam_client):
    client, mock_redis, _ = iam_client
    mock_redis.delete.side_effect = Exception("Redis is down")

    # Must not raise
    client.evict_cache("test-token")


# ---------------------------------------------------------------------------
# validate_remote
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_validate_remote_success(iam_client):
    client, mock_redis, mock_http = iam_client
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "valid": True,
        "user_id": "user1",
        "email": "user1@test.com",
        "roles": ["researcher"],
        "permissions": ["read"],
    }
    mock_http.post = AsyncMock(return_value=mock_response)

    result = await client.validate_remote("good-token")

    assert result is not None
    assert result.user_id == "user1"
    assert result.roles == ["researcher"]
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_validate_remote_invalid_token_evicts_cache(iam_client):
    client, mock_redis, mock_http = iam_client
    mock_response = MagicMock()
    mock_response.json.return_value = {"valid": False}
    mock_http.post = AsyncMock(return_value=mock_response)

    result = await client.validate_remote("bad-token")

    assert result is None
    mock_redis.delete.assert_called_once_with("iam:bad-token")


@pytest.mark.asyncio
async def test_validate_remote_network_error_returns_none(iam_client):
    client, _, mock_http = iam_client
    mock_http.post = AsyncMock(side_effect=Exception("network error"))

    result = await client.validate_remote("any-token")

    assert result is None


@pytest.mark.asyncio
async def test_validate_remote_uses_optional_fields(iam_client):
    client, mock_redis, mock_http = iam_client
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "valid": True,
        "user_id": "u2",
        "email": "u2@test.com",
        # no roles, no permissions
    }
    mock_http.post = AsyncMock(return_value=mock_response)

    result = await client.validate_remote("token2")

    assert result is not None
    assert result.roles == []
    assert result.permissions == []


# ---------------------------------------------------------------------------
# get_user  (main entry — cache-first)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_user_returns_cached_on_hit(iam_client):
    client, mock_redis, _ = iam_client
    user_data = {
        "user_id": "user1",
        "email": "u@t.com",
        "roles": [],
        "permissions": [],
        "valid": True,
    }
    mock_redis.get.return_value = json.dumps(user_data)

    result = await client.get_user("some-token", "secret")

    assert result.user_id == "user1"
    # No JWT decode should happen
    mock_redis.setex.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_jwt_path_on_cache_miss(iam_client):
    client, mock_redis, _ = iam_client
    mock_redis.get.return_value = None

    secret = "test-secret"
    payload = {
        "sub": "user2",
        "email": "user2@test.com",
        "roles": ["admin"],
        "permissions": ["write"],
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    result = await client.get_user(token, secret)

    assert result is not None
    assert result.user_id == "user2"
    assert result.email == "user2@test.com"
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_no_email_in_jwt_raises(iam_client):
    """email is required in UserContext — missing it propagates a ValidationError."""
    client, mock_redis, _ = iam_client
    mock_redis.get.return_value = None

    secret = "test-secret"
    payload = {"sub": "user3", "exp": int(time.time()) + 3600}
    token = jwt.encode(payload, secret, algorithm="HS256")

    with pytest.raises(Exception):
        await client.get_user(token, secret)


@pytest.mark.asyncio
async def test_get_user_invalid_jwt_returns_none(iam_client):
    client, mock_redis, _ = iam_client
    mock_redis.get.return_value = None

    result = await client.get_user("not-a-valid-jwt", "secret")

    assert result is None


@pytest.mark.asyncio
async def test_get_user_expired_jwt_returns_none(iam_client):
    client, mock_redis, _ = iam_client
    mock_redis.get.return_value = None

    secret = "test-secret"
    payload = {"sub": "user1", "exp": int(time.time()) - 100}
    token = jwt.encode(payload, secret, algorithm="HS256")

    result = await client.get_user(token, secret)

    assert result is None
