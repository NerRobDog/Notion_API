import pytest
from unittest.mock import Mock, patch, AsyncMock
from notion_client import Client, AsyncClient, APIResponseError
import httpx
from notion_client.errors import RequestTimeoutError


def test_client_initializes_with_default_options():
    client = Client()
    assert client.options.auth is None
    assert client.options.timeout_ms == 60_000
    assert client.options.base_url == "https://api.notion.com"


def test_client_initializes_with_custom_options():
    options = {
        "auth": "test-token",
        "timeout_ms": 30_000,
        "base_url": "https://test.notion.com"
    }
    client = Client(options)
    assert client.options.auth == "test-token"
    assert client.options.timeout_ms == 30_000
    assert client.options.base_url == "https://test.notion.com"


# def test_client_handles_retry_on_rate_limit():
#     with patch("httpx.Client") as mock_client:
#         mock_response = Mock()
#         mock_response.json.return_value = {"code": "rate_limited"}
#         mock_response.status_code = 429
#         mock_response.text = "Rate limited"
#         mock_client.return_value.send.side_effect = httpx.HTTPStatusError(
#             "Rate limited",
#             request=Mock(),
#             response=mock_response
#         )
#
#         client = Client({"auth": "test-token"})
#         with pytest.raises(APIResponseError) as exc:
#             client.request("test", "GET")
#         assert exc.value.code == "rate_limited"


@pytest.mark.asyncio
async def test_async_client_makes_successful_request():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_client.return_value.send.return_value = mock_response
        mock_client.return_value.send.side_effect = AsyncMock(return_value=mock_response)

        async with AsyncClient({"auth": "test-token"}) as client:
            result = await client.request("test", "GET")
            assert result == {"success": True}


def test_client_builds_correct_request_headers():
    client = Client({"auth": "test-token"})
    request = client._build_request("GET", "test")
    assert request.headers["Authorization"] == "Bearer test-token"
    assert "Notion-Version" in request.headers
    assert "User-Agent" in request.headers


def test_client_handles_timeout():
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.send.side_effect = httpx.TimeoutException("")
        client = Client()
        with pytest.raises(RequestTimeoutError):
            client.request("test", "GET")


# @pytest.mark.asyncio
# async def test_async_client_context_manager_closes_properly():
#     with patch("httpx.AsyncClient") as mock_client:
#         mock_client.return_value.aclose = AsyncMock()
#         async with AsyncClient() as client:
#             assert len(client._clients) == 2
#         await mock_client.return_value.aclose.assert_awaited_once()
