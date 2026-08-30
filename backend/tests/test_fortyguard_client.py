"""Tests for FortyGuardClient — request construction, auth, timeouts, error handling."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from app.services.fortyguard.client import (
    FortyGuardClient,
    FortyGuardAPIError,
    FortyGuardTimeoutError,
)


class TestFortyGuardClientAuth:
    """Authentication header is correctly applied."""

    @pytest.mark.asyncio
    async def test_auth_header_set_on_post(self):
        """api-key header must be included in every POST request."""
        client = FortyGuardClient("https://api.test.com", "my_secret_key", timeout=5)

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {"data": "ok"}
            mock_response.raise_for_status = MagicMock()
            mock_instance.post.return_value = mock_response
            mock_instance.aclose = AsyncMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            await client.post("/heatmap", json={"test": True})

            # Verify the client was created with the api-key header
            MockClient.assert_called_once()
            call_kwargs = MockClient.call_args[1]
            assert call_kwargs["headers"] == {"api-key": "my_secret_key"}

    @pytest.mark.asyncio
    async def test_auth_header_set_on_get(self):
        """api-key header must be included in every GET request."""
        client = FortyGuardClient("https://api.test.com", "my_secret_key", timeout=5)

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {"data": "ok"}
            mock_response.raise_for_status = MagicMock()
            mock_instance.get.return_value = mock_response
            mock_instance.aclose = AsyncMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            await client.get("/status/test-id")

            call_kwargs = MockClient.call_args[1]
            assert call_kwargs["headers"] == {"api-key": "my_secret_key"}

    def test_api_key_never_in_repr(self):
        """API key must not appear in string representations."""
        client = FortyGuardClient("https://api.test.com", "super_secret_key_12345")
        assert "super_secret_key_12345" not in repr(client)


class TestFortyGuardClientPost:
    """POST request handling."""

    @pytest.mark.asyncio
    async def test_successful_post_returns_json(self):
        client = FortyGuardClient("https://api.test.com", "key", timeout=5)

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "error": False,
                "data": {"activity_id": "abc-123"},
            }
            mock_response.raise_for_status = MagicMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            result = await client.post("/heatmap", json={"polygon": []})
            assert result["data"]["activity_id"] == "abc-123"

    @pytest.mark.asyncio
    async def test_post_timeout_raises_timeout_error(self):
        client = FortyGuardClient("https://api.test.com", "key", timeout=1)

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = httpx.TimeoutException("Connection timed out")
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            with pytest.raises(FortyGuardTimeoutError):
                await client.post("/heatmap", json={})

    @pytest.mark.asyncio
    async def test_post_http_error_raises_api_error(self):
        client = FortyGuardClient("https://api.test.com", "key", timeout=5)

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500", request=MagicMock(), response=mock_response
            )
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            with pytest.raises(FortyGuardAPIError):
                await client.post("/heatmap", json={})


class TestFortyGuardClientGet:
    """GET request handling."""

    @pytest.mark.asyncio
    async def test_successful_get_returns_json(self):
        client = FortyGuardClient("https://api.test.com", "key", timeout=5)

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "error": False,
                "data": {"status": "Completed", "result": {}},
            }
            mock_response.raise_for_status = MagicMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            result = await client.get("/status/test-uuid")
            assert result["data"]["status"] == "Completed"

    @pytest.mark.asyncio
    async def test_get_timeout_raises_timeout_error(self):
        client = FortyGuardClient("https://api.test.com", "key", timeout=1)

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = httpx.TimeoutException("timeout")
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            with pytest.raises(FortyGuardTimeoutError):
                await client.get("/status/test")

    @pytest.mark.asyncio
    async def test_get_http_error_raises_api_error(self):
        client = FortyGuardClient("https://api.test.com", "key", timeout=5)

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.text = "Not Found"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404", request=MagicMock(), response=mock_response
            )
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            with pytest.raises(FortyGuardAPIError):
                await client.get("/status/bad-id")

    @pytest.mark.asyncio
    async def test_malformed_json_raises_api_error(self):
        client = FortyGuardClient("https://api.test.com", "key", timeout=5)

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            with pytest.raises(FortyGuardAPIError):
                await client.get("/status/test")
