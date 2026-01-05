"""Tests for uncovered functions and edge cases in Mailgun MCP"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mailgun_mcp.main import (
    BasicAuth,
    _http_request,
    _normalize_auth_for_provider,
    get_mailgun_api_key,
    get_mailgun_domain,
    validate_api_key_at_startup,
)


def test_basic_auth_equality():
    """Test BasicAuth equality comparisons"""
    auth1 = BasicAuth("user", "pass")
    auth2 = BasicAuth("user", "pass")
    auth3 = BasicAuth("user", "different_pass")

    # Test equality with another BasicAuth instance
    assert auth1 == auth2
    assert not auth1 == auth3

    # Test equality with tuple
    assert auth1 == ("user", "pass")
    assert not auth1 == ("user", "different_pass")

    # Test equality with httpx BasicAuth-like object
    class MockAuth:
        def __init__(self, username, password):
            self.username = username
            self.password = password

    mock_auth = MockAuth("user", "pass")
    assert auth1 == mock_auth
    assert not auth1 == MockAuth("user", "different_pass")


def test_basic_auth_repr():
    """Test BasicAuth string representation"""
    auth = BasicAuth("test_user", "test_pass")
    assert "test_user" in repr(auth)
    assert "test_pass" in repr(auth)


def test_normalize_auth_for_provider_with_tuple():
    """Test _normalize_auth_for_provider with tuple auth"""
    import unittest.mock

    # Create a mock tuple with MagicMock elements to simulate test environment
    mock_username = unittest.mock.MagicMock()
    mock_password = unittest.mock.MagicMock()
    test_tuple = (mock_username, mock_password)

    kwargs = {"auth": test_tuple}
    result = _normalize_auth_for_provider(kwargs)

    # Should return the tuple as-is in test environment
    assert result["auth"] == test_tuple


def test_normalize_auth_for_provider_with_basic_auth():
    """Test _normalize_auth_for_provider with BasicAuth object"""
    auth = BasicAuth("test_user", "test_pass")
    kwargs = {"auth": auth}

    result = _normalize_auth_for_provider(kwargs)

    # Should convert BasicAuth to header format
    assert "headers" in result
    assert "Authorization" in result["headers"]
    assert result["headers"]["Authorization"].startswith("Basic ")


def test_normalize_auth_for_provider_without_auth():
    """Test _normalize_auth_for_provider without auth key"""
    kwargs = {"other_param": "value"}

    result = _normalize_auth_for_provider(kwargs)

    # Should return unchanged kwargs
    assert result == kwargs


@pytest.mark.asyncio
async def test_http_request_get():
    """Test _http_request with GET method"""
    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_instance.get.return_value = mock_response

        result = await _http_request("GET", "https://example.com")

        mock_instance.get.assert_called_once()
        assert result == mock_response


@pytest.mark.asyncio
async def test_http_request_post():
    """Test _http_request with POST method"""
    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_instance.post.return_value = mock_response

        result = await _http_request("POST", "https://example.com", data={"key": "value"})

        mock_instance.post.assert_called_once()
        assert result == mock_response


@pytest.mark.asyncio
async def test_http_request_put():
    """Test _http_request with PUT method"""
    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_instance.put.return_value = mock_response

        result = await _http_request("PUT", "https://example.com", data={"key": "value"})

        mock_instance.put.assert_called_once()
        assert result == mock_response


@pytest.mark.asyncio
async def test_http_request_delete():
    """Test _http_request with DELETE method"""
    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_instance.delete.return_value = mock_response

        result = await _http_request("DELETE", "https://example.com")

        mock_instance.delete.assert_called_once()
        assert result == mock_response


@pytest.mark.asyncio
async def test_http_request_other_method():
    """Test _http_request with other HTTP method"""
    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_instance.request.return_value = mock_response

        result = await _http_request("PATCH", "https://example.com", data={"key": "value"})

        mock_instance.request.assert_called_once()
        assert result == mock_response


def test_validate_api_key_at_startup_missing(monkeypatch, capsys):
    """Test validate_api_key_at_startup when API key is missing"""
    monkeypatch.setenv("MAILGUN_API_KEY", "")

    with pytest.raises(SystemExit):
        validate_api_key_at_startup()

    captured = capsys.readouterr()
    assert "MAILGUN_API_KEY environment variable is not set" in captured.err


def test_validate_api_key_at_startup_too_short(monkeypatch, capsys):
    """Test validate_api_key_at_startup when API key is too short"""
    monkeypatch.setenv("MAILGUN_API_KEY", "short")

    with pytest.raises(SystemExit):
        validate_api_key_at_startup()

    captured = capsys.readouterr()
    assert "appears too short" in captured.err


def test_validate_api_key_at_startup_valid(monkeypatch):
    """Test validate_api_key_at_startup with valid API key"""
    monkeypatch.setenv("MAILGUN_API_KEY", "key-" + "a" * 30)  # Valid length

    # Should not raise SystemExit
    validate_api_key_at_startup()


def test_get_mailgun_api_key():
    """Test get_mailgun_api_key function"""
    import os

    # Test with key set
    os.environ["MAILGUN_API_KEY"] = "test-key"
    assert get_mailgun_api_key() == "test-key"

    # Test without key set
    if "MAILGUN_API_KEY" in os.environ:
        del os.environ["MAILGUN_API_KEY"]
    assert get_mailgun_api_key() is None


def test_get_mailgun_domain():
    """Test get_mailgun_domain function"""
    import os

    # Test with domain set
    os.environ["MAILGUN_DOMAIN"] = "test-domain.com"
    assert get_mailgun_domain() == "test-domain.com"

    # Test without domain set
    if "MAILGUN_DOMAIN" in os.environ:
        del os.environ["MAILGUN_DOMAIN"]
    assert get_mailgun_domain() is None
