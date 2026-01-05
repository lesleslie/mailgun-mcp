"""Additional tests for uncovered Mailgun MCP functions"""
from unittest.mock import AsyncMock, patch

import pytest

from mailgun_mcp.main import (
    add_complaint,
    add_unsubscribe,
    delete_complaint,
    delete_domain,
    delete_route,
    delete_template,
    delete_unsubscribe,
    delete_webhook,
    get_complaints,
    get_route,
    get_template,
    get_unsubscribes,
    get_webhook,
    update_route,
    update_template,
    verify_domain,
)


# Tests for domain management tools
def test_delete_domain_requires_api_key(monkeypatch):
    """Test that delete_domain fails when API key is not set"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: None)

    import asyncio

    async def run_test():
        result = await delete_domain.run({"domain_name": "example.com"})
        if hasattr(result, "structured_content"):
            return result.structured_content
        else:
            return result

    result = asyncio.run(run_test())

    assert "error" in result
    assert result["error"]["type"] == "configuration_error"
    assert (
        "MAILGUN_API_KEY environment variable is not set." in result["error"]["message"]
    )


@pytest.mark.asyncio
async def test_delete_domain_with_mock_response(monkeypatch):
    """Test delete_domain with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"domain": {"name": "deleted-domain.com", "state": "deleted"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_domain.run({"domain_name": "deleted-domain.com"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "domain" in result
        assert result["domain"]["name"] == "deleted-domain.com"
        instance.delete.assert_called_once()


def test_verify_domain_requires_api_key(monkeypatch):
    """Test that verify_domain fails when API key is not set"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: None)

    import asyncio

    async def run_test():
        result = await verify_domain.run({"domain_name": "example.com"})
        if hasattr(result, "structured_content"):
            return result.structured_content
        else:
            return result

    result = asyncio.run(run_test())

    assert "error" in result
    assert result["error"]["type"] == "configuration_error"
    assert (
        "MAILGUN_API_KEY environment variable is not set." in result["error"]["message"]
    )


@pytest.mark.asyncio
async def test_verify_domain_with_mock_response(monkeypatch):
    """Test verify_domain with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"domain": {"name": "verified-domain.com", "state": "active"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.put.return_value = mock_response

        result = await verify_domain.run({"domain_name": "verified-domain.com"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "domain" in result
        assert result["domain"]["name"] == "verified-domain.com"
        instance.put.assert_called_once()


# Tests for complaint management tools
def test_get_complaints_requires_api_key(monkeypatch):
    """Test that get_complaints fails when API key is not set"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: None)

    import asyncio

    async def run_test():
        result = await get_complaints.run({"domain_name": "example.com", "limit": 10})
        if hasattr(result, "structured_content"):
            return result.structured_content
        else:
            return result

    result = asyncio.run(run_test())

    assert "error" in result
    assert result["error"]["type"] == "configuration_error"
    assert (
        "MAILGUN_API_KEY environment variable is not set." in result["error"]["message"]
    )


@pytest.mark.asyncio
async def test_get_complaints_with_mock_response(monkeypatch):
    """Test get_complaints with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"items": [{"address": "complainer@example.com"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_complaints.run({"domain_name": "example.com", "limit": 10})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "items" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_add_complaint_with_mock_response(monkeypatch):
    """Test add_complaint with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"address": "complainer@example.com", "created_at": "2023-01-01"}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await add_complaint.run(
            {"domain_name": "example.com", "address": "complainer@example.com"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "address" in result
        assert result["address"] == "complainer@example.com"
        instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_delete_complaint_with_mock_response(monkeypatch):
    """Test delete_complaint with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"address": "complainer@example.com", "deleted": True}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_complaint.run(
            {"domain_name": "example.com", "address": "complainer@example.com"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "deleted" in result
        instance.delete.assert_called_once()


# Tests for unsubscribe management tools
@pytest.mark.asyncio
async def test_get_unsubscribes_with_mock_response(monkeypatch):
    """Test get_unsubscribes with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"items": [{"address": "unsubscribed@example.com"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_unsubscribes.run({"domain_name": "example.com", "limit": 10})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "items" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_add_unsubscribe_with_mock_response(monkeypatch):
    """Test add_unsubscribe with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"address": "unsubscribed@example.com", "tag": "all"}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await add_unsubscribe.run(
            {"domain_name": "example.com", "address": "unsubscribed@example.com", "tag": "all"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "address" in result
        assert result["address"] == "unsubscribed@example.com"
        instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_delete_unsubscribe_with_mock_response(monkeypatch):
    """Test delete_unsubscribe with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"address": "unsubscribed@example.com", "deleted": True}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_unsubscribe.run(
            {"domain_name": "example.com", "address": "unsubscribed@example.com", "tag": "all"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "deleted" in result
        instance.delete.assert_called_once()


# Tests for route management tools
@pytest.mark.asyncio
async def test_get_route_with_mock_response(monkeypatch):
    """Test get_route with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"route": {"id": "route1", "priority": 10}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_route.run({"route_id": "route1"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "route" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_update_route_with_mock_response(monkeypatch):
    """Test update_route with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"route": {"id": "route1", "priority": 20}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.put.return_value = mock_response

        result = await update_route.run(
            {"route_id": "route1", "priority": 20, "expression": "match_recipient('.*@example.com')"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "route" in result
        instance.put.assert_called_once()


@pytest.mark.asyncio
async def test_delete_route_with_mock_response(monkeypatch):
    """Test delete_route with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"route": {"id": "route1", "deleted": True}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_route.run({"route_id": "route1"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "route" in result
        assert result["route"]["deleted"] is True
        instance.delete.assert_called_once()


# Tests for template management tools
@pytest.mark.asyncio
async def test_get_template_with_mock_response(monkeypatch):
    """Test get_template with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"template": {"name": "welcome-template", "version": "v1"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_template.run({"template_name": "welcome-template"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "template" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_update_template_with_mock_response(monkeypatch):
    """Test update_template with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"template": {"name": "welcome-template", "version": "v2"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.put.return_value = mock_response

        result = await update_template.run(
            {
                "template_name": "welcome-template",
                "template_version_name": "v2",
                "template_version_subject": "Updated Welcome!",
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "template" in result
        instance.put.assert_called_once()


@pytest.mark.asyncio
async def test_delete_template_with_mock_response(monkeypatch):
    """Test delete_template with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"template": {"name": "welcome-template", "deleted": True}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_template.run({"template_name": "welcome-template"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "template" in result
        assert result["template"]["deleted"] is True
        instance.delete.assert_called_once()


# Tests for webhook management tools
@pytest.mark.asyncio
async def test_get_webhook_with_mock_response(monkeypatch):
    """Test get_webhook with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"webhook": {"url": "https://example.com/webhook"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_webhook.run({"webhook_type": "click"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "webhook" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_delete_webhook_with_mock_response(monkeypatch):
    """Test delete_webhook with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"webhook_type": "click", "deleted": True}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_webhook.run({"webhook_type": "click"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "deleted" in result
        instance.delete.assert_called_once()
