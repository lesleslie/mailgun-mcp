from unittest.mock import AsyncMock, patch

import pytest

from mailgun_mcp.main import (
    add_bounce,
    create_domain,
    create_route,
    create_template,
    create_webhook,
    delete_bounce,
    get_bounces,
    get_domain,
    get_domains,
    get_events,
    get_routes,
    get_stats,
    get_templates,
    get_webhooks,
    send_message,
)


def test_send_message_tool_exists():
    """Test that the send_message tool is available"""
    assert send_message.name == "send_message"


def test_send_message_requires_credentials(monkeypatch):
    """Test that send_message fails when credentials are not set"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: None)
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_domain", lambda: None)

    import asyncio

    # Use the run method of the FunctionTool
    async def run_test():
        result = await send_message.run(
            {
                "from_email": "sender@example.com",
                "to": "recipient@example.com",
                "subject": "Hello",
                "text": "Test message",
            }
        )
        # Extract the actual result from the ToolResult
        if hasattr(result, "structured_content"):
            return result.structured_content
        else:
            return result

    result = asyncio.run(run_test())

    assert "error" in result
    assert result["error"]["type"] == "configuration_error"
    assert (
        "MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables are not set."
        in result["error"]["message"]
    )


def test_send_message_missing_one_credential(monkeypatch):
    """Test that send_message fails when only one credential is set"""
    import asyncio

    # Test with only API key set
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_domain", lambda: None)

    async def run_test():
        result = await send_message.run(
            {
                "from_email": "sender@example.com",
                "to": "recipient@example.com",
                "subject": "Hello",
                "text": "Test message",
            }
        )
        # Extract the actual result from the ToolResult
        if hasattr(result, "structured_content"):
            return result.structured_content
        else:
            return result

    result = asyncio.run(run_test())
    assert "error" in result
    assert result["error"]["type"] == "configuration_error"

    # Test with only domain set
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: None)
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_domain", lambda: "example.com")

    result = asyncio.run(run_test())
    assert "error" in result
    assert result["error"]["type"] == "configuration_error"


@pytest.mark.asyncio
async def test_send_message_with_all_required_fields(monkeypatch):
    """Test send_message with mock Mailgun response"""
    # Mock the environment variables in the main module
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_domain", lambda: "example.com")

    # Create a mock response
    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"status": "sent", "id": "msg123"}

    # Mock the httpx AsyncClient context manager and its post method
    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        # Configure the mock to properly handle the async context manager protocol
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        MockAsyncClient.return_value.__aenter__.return_value = mock_client_instance

        result = await send_message.run(
            {
                "from_email": "sender@example.com",
                "to": "recipient@example.com",
                "subject": "Test Subject",
                "text": "Test message content",
            }
        )

        # Extract actual result from ToolResult if needed
        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert result == {"status": "sent", "id": "msg123"}
        # Verify the call to Mailgun was made with correct parameters
        mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_with_optional_fields(monkeypatch):
    """Test send_message with optional fields like CC, BCC, and HTML"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_domain", lambda: "example.com")

    # Create a mock response that is not a coroutine
    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"status": "queued"}

    # Track what data was sent to Mailgun
    captured_request_data = {}

    async def capture_post(url, auth, data):
        captured_request_data.update(data)
        return mock_response

    # Mock the httpx AsyncClient context manager and its post method
    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        # Configure the mock to call our capture_post function when post is called
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.side_effect = capture_post

        result = await send_message.run(
            {
                "from_email": "sender@example.com",
                "to": "recipient@example.com",
                "cc": "cc@example.com",
                "bcc": "bcc@example.com",
                "subject": "Test with CC/BCC",
                "text": "Test message with CC and BCC",
                "html": "<p>HTML content</p>",
            }
        )

        # Extract actual result from ToolResult if needed
        if hasattr(result, "structured_content"):
            result = result.structured_content

        # Verify that optional fields are included in the request to Mailgun
        assert captured_request_data["cc"] == "cc@example.com"
        assert captured_request_data["bcc"] == "bcc@example.com"
        assert captured_request_data["html"] == "<p>HTML content</p>"


@pytest.mark.asyncio
async def test_send_message_forwards_payload(monkeypatch):
    """Test that send_message forwards the correct payload to Mailgun"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_domain", lambda: "example.com")

    # Track the request made to Mailgun
    captured_request = {"url": None, "auth": None, "data": None}

    # Create a mock response that is not a coroutine
    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"status": "queued"}

    async def capture_post(url, auth, data):
        captured_request["url"] = url
        captured_request["auth"] = auth
        captured_request["data"] = dict(data)  # Convert FormData to dict
        return mock_response

    # Mock the httpx AsyncClient context manager and its post method
    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.side_effect = capture_post

        result = await send_message.run(
            {
                "from_email": "excited@example.com",
                "to": "user@example.com",
                "subject": "Hello",
                "text": "Testing",
            }
        )

        # Extract actual result from ToolResult if needed
        if hasattr(result, "structured_content"):
            result = result.structured_content

        # Check that the request was sent to the correct Mailgun endpoint
        expected_url = "https://api.mailgun.net/v3/example.com/messages"
        assert captured_request["url"] == expected_url
        assert captured_request["auth"] == ("api", "test-key")
        assert captured_request["data"] == {
            "from": "excited@example.com",
            "to": "user@example.com",
            "subject": "Hello",
            "text": "Testing",
        }


@pytest.mark.asyncio
async def test_send_message_handles_mailgun_error(monkeypatch):
    """Test that send_message handles Mailgun API errors properly"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_domain", lambda: "example.com")

    # Create a mock response that simulates an error
    mock_response = AsyncMock()
    mock_response.is_success = False
    mock_response.status_code = 400
    mock_response.text = "Bad request"

    # Mock the httpx AsyncClient context manager and its post method
    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await send_message.run(
            {
                "from_email": "invalid-email",
                "to": "recipient@example.com",
                "subject": "Test",
                "text": "Test",
            }
        )

        # Extract actual result from ToolResult if needed
        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "error" in result
        assert result["error"]["type"] == "mailgun_error"
        assert "400" in result["error"]["message"]


# Tests for domain management tools
def test_get_domains_requires_api_key(monkeypatch):
    """Test that get_domains fails when API key is not set"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: None)

    import asyncio

    async def run_test():
        result = await get_domains.run({})
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
async def test_get_domains_with_mock_response(monkeypatch):
    """Test get_domains with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"items": [], "total_count": 0}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_domains.run({"limit": 10, "skip": 0})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert result == {"items": [], "total_count": 0}
        instance.get.assert_called_once()


def test_get_domain_requires_api_key(monkeypatch):
    """Test that get_domain fails when API key is not set"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: None)

    import asyncio

    async def run_test():
        result = await get_domain.run({"domain_name": "example.com"})
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
async def test_create_domain_with_mock_response(monkeypatch):
    """Test create_domain with mock Mailgun response"""
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
                "wildcard": False,
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "domain" in result
        assert result["domain"]["name"] == "newdomain.com"
        instance.post.assert_called_once()


# Tests for events and stats tools
@pytest.mark.asyncio
async def test_get_events_with_mock_response(monkeypatch):
    """Test get_events with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {
        "items": [{"timestamp": 1234567890, "event": "delivered"}]
    }

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_events.run({"domain_name": "example.com", "limit": 10})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "items" in result
        assert len(result["items"]) == 1
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_stats_with_mock_response(monkeypatch):
    """Test get_stats with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {
        "stats": [{"time": "2023-01-01", "delivered": {"total": 5}}]
    }

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_stats.run(
            {
                "domain_name": "example.com",
                "event": ["delivered"],
                "start": "2023-01-01",
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "stats" in result
        assert len(result["stats"]) == 1
        instance.get.assert_called_once()


# Tests for suppression management tools
@pytest.mark.asyncio
async def test_get_bounces_with_mock_response(monkeypatch):
    """Test get_bounces with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"items": [{"address": "bounced@example.com"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_bounces.run({"domain_name": "example.com", "limit": 10})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "items" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_add_bounce_with_mock_response(monkeypatch):
    """Test add_bounce with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"address": "bounce@example.com", "code": 550}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await add_bounce.run(
            {"domain_name": "example.com", "address": "bounce@example.com"}
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


# Tests for route management tools
@pytest.mark.asyncio
async def test_get_routes_with_mock_response(monkeypatch):
    """Test get_routes with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {
        "routes": [{"id": "route1", "expression": "match_recipient('.*@example.com')"}]
    }

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_routes.run({"limit": 10})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "routes" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_route_with_mock_response(monkeypatch):
    """Test create_route with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"route": {"id": "newroute", "priority": 10}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await create_route.run(
            {
                "priority": 10,
                "expression": "match_recipient('.*@example.com')",
                "action": ["forward('http://example.com')"],
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "route" in result
        instance.post.assert_called_once()


# Tests for template management tools
@pytest.mark.asyncio
async def test_get_templates_with_mock_response(monkeypatch):
    """Test get_templates with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"templates": [{"name": "welcome-template"}]}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_templates.run({"limit": 10})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "templates" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_template_with_mock_response(monkeypatch):
    """Test create_template with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"template": {"name": "new-template"}}

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await create_template.run(
            {
                "name": "welcome-template",
                "subject": "Welcome!",
                "template_text": "Welcome to our service, {{name}}!",
            }
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "template" in result
        instance.post.assert_called_once()


# Tests for webhook management tools
@pytest.mark.asyncio
async def test_get_webhooks_with_mock_response(monkeypatch):
    """Test get_webhooks with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {
        "webhooks": {"click": {"url": "https://example.com/webhooks/click"}}
    }

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.get.return_value = mock_response

        result = await get_webhooks.run({})

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "webhooks" in result
        instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_webhook_with_mock_response(monkeypatch):
    """Test create_webhook with mock Mailgun response"""
    monkeypatch.setattr("mailgun_mcp.main.get_mailgun_api_key", lambda: "test-key")

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.json.return_value = {
        "webhook": {"url": "https://example.com/webhooks/click"}
    }

    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        instance.post.return_value = mock_response

        result = await create_webhook.run(
            {"webhook_type": "click", "url": "https://example.com/webhooks/click"}
        )

        if hasattr(result, "structured_content"):
            result = result.structured_content

        assert "webhook" in result
        instance.post.assert_called_once()
