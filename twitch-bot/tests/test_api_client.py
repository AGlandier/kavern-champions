import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from api.client import get_latest_battleroom, battleroom_enter


def make_mock_client(method, response):
    mock_client = AsyncMock()
    getattr(mock_client, method).return_value = response
    return mock_client


def make_response(status_code, json_body=None):
    r = MagicMock()
    r.status_code = status_code
    r.json.return_value = json_body or {}
    return r


# --- get_latest_battleroom ---

async def test_get_latest_battleroom_returns_json():
    mock_client = make_mock_client("get", make_response(200, {"id": 1, "name": "TestRoom"}))
    with patch("api.client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = mock_client
        result = await get_latest_battleroom()
    assert result == {"id": 1, "name": "TestRoom"}


async def test_get_latest_battleroom_404_returns_none():
    mock_client = make_mock_client("get", make_response(404))
    with patch("api.client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = mock_client
        result = await get_latest_battleroom()
    assert result is None


async def test_get_latest_battleroom_connect_error_returns_none():
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.ConnectError("Connection refused")
    with patch("api.client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = mock_client
        result = await get_latest_battleroom()
    assert result is None


async def test_get_latest_battleroom_timeout_returns_none():
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.TimeoutException("timed out")
    with patch("api.client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = mock_client
        result = await get_latest_battleroom()
    assert result is None


# --- battleroom_enter ---

async def test_battleroom_enter_success_returns_status_and_body():
    mock_client = make_mock_client("post", make_response(200, {"message": "ok"}))
    with patch("api.client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = mock_client
        result = await battleroom_enter(1, "testuser")
    assert result == {"status": 200, "body": {"message": "ok"}}


async def test_battleroom_enter_409_returns_status_and_body():
    mock_client = make_mock_client("post", make_response(409, {"error": "already registered"}))
    with patch("api.client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = mock_client
        result = await battleroom_enter(1, "testuser")
    assert result == {"status": 409, "body": {"error": "already registered"}}


async def test_battleroom_enter_network_error_returns_none():
    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.TimeoutException("timed out")
    with patch("api.client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = mock_client
        result = await battleroom_enter(1, "testuser")
    assert result is None


async def test_battleroom_enter_sends_correct_payload():
    mock_client = make_mock_client("post", make_response(200, {}))
    with patch("api.client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = mock_client
        await battleroom_enter(42, "alice")
    mock_client.post.assert_awaited_once()
    _, kwargs = mock_client.post.call_args
    assert kwargs["json"] == {"battleroom_id": 42, "username": "alice"}
