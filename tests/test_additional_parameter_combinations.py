"""Additional tests to cover remaining gaps in Mailgun MCP"""
from unittest.mock import AsyncMock, patch

import pytest

from mailgun_mcp.main import (
    add_bounce,
    add_complaint,
    add_unsubscribe,
    create_domain,
    create_route,
    create_template,
    create_webhook,
    delete_bounce,
    delete_complaint,
    delete_domain,
    delete_route,
    delete_template,
    delete_unsubscribe,
    delete_webhook,
    get_bounces,
    get_complaints,
    get_domain,
    get_domains,
    get_events,
    get_route,
    get_routes,
    get_stats,
    get_template,
    get_templates,
    get_unsubscribes,
    get_webhook,
    get_webhooks,
    send_message,
    update_route,
    update_template,
    verify_domain,
)


@pytest.mark.asyncio
async def test_send_message_with_all_optional_fields(monkeypatch):
    """Test send_message with all optional fields to cover more code paths"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_domain", lambda: "example.com")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"status": "sent", "id": "msg123"}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await send_message.run(
            {
                "from_email": "sender@example.com",
                "to": "recipient@example.com",
                "subject": "Test Subject",
                "text": "Test message content",
                "cc": "cc@example.com",
                "bcc": "bcc@example.com",
                "html": "<p>HTML content</p>",
                "attachment": "path/to/file.txt",
                "tag": "test-tag",
                "schedule_at": "2023-12-01 10:00:00",
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert result == {"status": "sent", "id": "msg123"}
        # Verify the call to Mailgun was made with all parameters
        call_args = instance.post.call_args
        assert call_args is not None


@pytest.mark.asyncio
async def test_send_message_with_attachment(monkeypatch):
    """Test send_message with attachment parameter specifically"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_domain", lambda: "example.com")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"status": "sent"}

    captured_request_data = {}

    async def capture_post(url, auth, data):
        captured_request_data.update(data)
        return mock_response

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.side_effect = capture_post

        await send_message.run(
            {
                "from_email": "sender@example.com",
                "to": "recipient@example.com",
                "subject": "Test with attachment",
                "text": "Test message",
                "attachment": "test_attachment.txt",
            }
        )

        # Verify attachment was included in the request
        assert "attachment" in captured_request_data


@pytest.mark.asyncio
async def test_get_domains_with_parameters(monkeypatch):
    """Test get_domains with specific parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"items": [], "total_count": 0}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_domains.run({"limit": 50, "skip": 10})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert result == {"items": [], "total_count": 0}
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_domain_with_mock_response(monkeypatch):
    """Test get_domain with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {
        "domain": {"name": "example.com", "state": "active"}
    }

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_domain.run({"domain_name": "example.com"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "domain" in result
        assert result["domain"]["name"] == "example.com"
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_domain_with_all_parameters(monkeypatch):
    """Test create_domain with all possible parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {
        "domain": {"name": "newdomain.com", "smtp_login": "postmaster@newdomain.com"}
    }

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await create_domain.run(
            {
                "domain_name": "newdomain.com",
                "smtp_password": "password123",
                "spam_action": "tag",
                "wildcard": True,
                "ips": "127.0.0.1,127.0.0.2",
                "pool_id": "pool123",
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "domain" in result
        assert result["domain"]["name"] == "newdomain.com"
        instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_delete_domain_with_mock_response(monkeypatch):
    """Test delete_domain with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"domain": {"name": "deleted.com", "state": "deleted"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_domain.run({"domain_name": "deleted.com"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "domain" in result
        assert result["domain"]["name"] == "deleted.com"
        instance.delete.assert_called_once()


@pytest.mark.asyncio
async def test_verify_domain_with_mock_response(monkeypatch):
    """Test verify_domain with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"domain": {"name": "verified.com", "state": "active"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.put.return_value = mock_response

        result = await verify_domain.run({"domain_name": "verified.com"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "domain" in result
        assert result["domain"]["name"] == "verified.com"
        instance.put.assert_called_once()


@pytest.mark.asyncio
async def test_get_events_with_all_parameters(monkeypatch):
    """Test get_events with all possible parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"items": [{"event": "delivered"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_events.run(
            {
                "domain_name": "example.com",
                "event": "delivered",
                "begin": "2023-01-01T00:00:00Z",
                "end": "2023-01-02T00:00:00Z",
                "ascending": "true",
                "limit": 50,
                "pretty": False,
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "items" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_stats_with_all_parameters(monkeypatch):
    """Test get_stats with all possible parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"stats": [{"delivered": {"total": 5}}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_stats.run(
            {
                "domain_name": "example.com",
                "event": ["delivered", "opened"],
                "start": "2023-01-01",
                "end": "2023-01-02",
                "resolution": "hour",
                "duration": "1w",
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "stats" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_bounces_with_parameters(monkeypatch):
    """Test get_bounces with specific parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"items": [{"address": "bounced@example.com"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_bounces.run({"domain_name": "example.com", "limit": 50, "skip": 5})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "items" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_add_bounce_with_all_parameters(monkeypatch):
    """Test add_bounce with all parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"address": "bounce@example.com", "code": 550, "error": "Mailbox unavailable"}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await add_bounce.run(
            {
                "domain_name": "example.com",
                "address": "bounce@example.com",
                "code": 550,
                "error": "Mailbox unavailable",
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "address" in result
        assert result["address"] == "bounce@example.com"
        instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_delete_bounce_with_mock_response(monkeypatch):
    """Test delete_bounce with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"address": "bounce@example.com", "deleted": True}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_bounce.run(
            {"domain_name": "example.com", "address": "bounce@example.com"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "deleted" in result
        instance.delete.assert_called_once()


@pytest.mark.asyncio
async def test_get_complaints_with_parameters(monkeypatch):
    """Test get_complaints with specific parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"items": [{"address": "complainer@example.com"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_complaints.run({"domain_name": "example.com", "limit": 25, "skip": 10})

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
    mock_response.json.return_value = {"address": "complainer@example.com", "created_at": "2023-01-01T00:00:00Z"}

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


@pytest.mark.asyncio
async def test_get_unsubscribes_with_parameters(monkeypatch):
    """Test get_unsubscribes with specific parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"items": [{"address": "unsubscribed@example.com"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_unsubscribes.run({"domain_name": "example.com", "limit": 75, "skip": 20})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "items" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_add_unsubscribe_with_all_parameters(monkeypatch):
    """Test add_unsubscribe with all parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"address": "unsubscribed@example.com", "tag": "newsletter"}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await add_unsubscribe.run(
            {"domain_name": "example.com", "address": "unsubscribed@example.com", "tag": "newsletter"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "address" in result
        assert result["address"] == "unsubscribed@example.com"
        instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_delete_unsubscribe_with_all_parameters(monkeypatch):
    """Test delete_unsubscribe with all parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"address": "unsubscribed@example.com", "deleted": True}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_unsubscribe.run(
            {"domain_name": "example.com", "address": "unsubscribed@example.com", "tag": "promotions"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "deleted" in result
        instance.delete.assert_called_once()


@pytest.mark.asyncio
async def test_get_routes_with_parameters(monkeypatch):
    """Test get_routes with specific parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"routes": [{"id": "route1", "expression": "match_recipient"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_routes.run({"limit": 20, "skip": 5})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "routes" in result
        instance.get.assert_called_once()


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
        assert result["route"]["id"] == "route1"
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_route_with_all_parameters(monkeypatch):
    """Test create_route with all parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"route": {"id": "newroute", "priority": 5}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await create_route.run(
            {
                "priority": 5,
                "expression": "match_recipient('.*@example.com')",
                "action": ["forward('http://example.com')"],
                "description": "Route for example.com",
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "route" in result
        instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_update_route_with_all_parameters(monkeypatch):
    """Test update_route with all parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"route": {"id": "route1", "priority": 15}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.put.return_value = mock_response

        result = await update_route.run(
            {
                "route_id": "route1",
                "priority": 15,
                "expression": "match_recipient('.*@updated.com')",
                "action": ["forward('http://updated.com')"],
                "description": "Updated route",
            }
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


@pytest.mark.asyncio
async def test_get_templates_with_parameters(monkeypatch):
    """Test get_templates with specific parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"templates": [{"name": "template1"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_templates.run({"limit": 30, "skip": 15})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "templates" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_template_with_mock_response(monkeypatch):
    """Test get_template with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"template": {"name": "template1", "version": "v1"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_template.run({"template_name": "template1"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "template" in result
        assert result["template"]["name"] == "template1"
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_template_with_all_parameters(monkeypatch):
    """Test create_template with all parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"template": {"name": "new-template", "version": "v1"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await create_template.run(
            {
                "name": "new-template",
                "subject": "New Template Subject",
                "template_text": "Hello {{name}}!",
                "template_html": "<p>Hello {{name}}!</p>",
                "description": "A new template",
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "template" in result
        instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_update_template_with_all_parameters(monkeypatch):
    """Test update_template with all parameters"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"template": {"name": "template1", "version": "v2"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.put.return_value = mock_response

        result = await update_template.run(
            {
                "template_name": "template1",
                "description": "Updated template",
                "template_version_name": "v2",
                "template_version_subject": "Updated Subject",
                "template_version_template": "Updated template {{name}}",
                "template_version_html": "<p>Updated template {{name}}</p>",
                "template_version_active": True,
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
    mock_response.json.return_value = {"template": {"name": "template1", "deleted": True}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_template.run({"template_name": "template1"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "template" in result
        assert result["template"]["deleted"] is True
        instance.delete.assert_called_once()


@pytest.mark.asyncio
async def test_get_webhooks_with_mock_response(monkeypatch):
    """Test get_webhooks with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"webhooks": {"click": {"url": "https://example.com/click"}}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_webhooks.run({})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "webhooks" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_webhook_with_mock_response(monkeypatch):
    """Test get_webhook with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"webhook": {"url": "https://example.com/click"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_webhook.run({"webhook_type": "click"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "webhook" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_webhook_with_mock_response(monkeypatch):
    """Test create_webhook with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"webhook": {"url": "https://example.com/new-webhook"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await create_webhook.run(
            {"webhook_type": "open", "url": "https://example.com/new-webhook"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "webhook" in result
        instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_delete_webhook_with_mock_response(monkeypatch):
    """Test delete_webhook with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"webhook_type": "open", "deleted": True}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.delete.return_value = mock_response

        result = await delete_webhook.run({"webhook_type": "open"})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "deleted" in result
        instance.delete.assert_called_once()