#!/usr/bin/env python3
"""Comprehensive tests for Mailgun MCP API functions.

This test file provides coverage for email sending, attachments, and API mocking.
Tests are organized by functionality and use proper mocking of the Mailgun API.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mailgun_mcp.main import (
    BasicAuth,
    _http_request,
    _normalize_auth_for_provider,
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
    get_mailgun_api_key,
    get_mailgun_domain,
    get_masked_api_key,
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


class TestBasicAuth:
    """Test BasicAuth custom class."""

    def test_basic_auth_tuple_comparison(self):
        """Test BasicAuth equality with tuple."""
        auth = BasicAuth("user", "pass")
        assert auth == ("user", "pass")

    def test_basic_auth_object_comparison(self):
        """Test BasicAuth equality with another BasicAuth."""
        auth1 = BasicAuth("user", "pass")
        auth2 = BasicAuth("user", "pass")
        assert auth1 == auth2

    def test_basic_auth_inequality(self):
        """Test BasicAuth inequality."""
        auth1 = BasicAuth("user1", "pass1")
        auth2 = BasicAuth("user2", "pass2")
        assert auth1 != auth2

    def test_basic_auth_repr(self):
        """Test BasicAuth repr."""
        auth = BasicAuth("user", "pass")
        assert repr(auth) == "BasicAuth(username='user', password='pass')"


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_masked_api_key_no_key(self, monkeypatch):
        """Test get_masked_api_key when no key is set."""
        monkeypatch.setenv("MAILGUN_API_KEY", "")
        assert get_masked_api_key() == "***"

    def test_get_masked_api_key_short_key(self, monkeypatch):
        """Test get_masked_api_key with short key (5 chars)."""
        monkeypatch.setenv("MAILGUN_API_KEY", "short")
        assert get_masked_api_key() == "...hort"

    def test_get_masked_api_key_normal_key(self, monkeypatch):
        """Test get_masked_api_key with normal key."""
        monkeypatch.setenv("MAILGUN_API_KEY", "key-with-more-than-four-chars")
        assert get_masked_api_key() == "...hars"

    def test_get_mailgun_api_key_from_env(self, monkeypatch):
        """Test get_mailgun_api_key retrieves from environment."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key-123")
        assert get_mailgun_api_key() == "test-key-123"

    def test_get_mailgun_domain_from_env(self, monkeypatch):
        """Test get_mailgun_domain retrieves from environment."""
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")
        assert get_mailgun_domain() == "example.com"


class TestNormalizeAuth:
    """Test auth normalization for provider compatibility."""

    def test_normalize_auth_no_auth(self):
        """Test normalize when no auth present."""
        kwargs = {"data": {"key": "value"}}
        result = _normalize_auth_for_provider(kwargs)
        assert result == kwargs

    def test_normalize_auth_with_tuple(self):
        """Test normalize with tuple auth."""
        kwargs = {"auth": ("user", "pass")}
        result = _normalize_auth_for_provider(kwargs)
        assert "headers" in result
        assert "Authorization" in result["headers"]
        assert result["headers"]["Authorization"].startswith("Basic ")

    def test_normalize_auth_with_basic_auth(self):
        """Test normalize with BasicAuth object."""
        auth = BasicAuth("user", "pass")
        kwargs = {"auth": auth}
        result = _normalize_auth_for_provider(kwargs)
        assert "headers" in result
        assert "Authorization" in result["headers"]


class TestSendMessage:
    """Test send_message function."""

    @pytest.mark.asyncio
    async def test_send_message_missing_credentials(self, monkeypatch):
        """Test send_message fails without credentials."""
        monkeypatch.setenv("MAILGUN_API_KEY", "")
        monkeypatch.setenv("MAILGUN_DOMAIN", "")

        result = await send_message(
            from_email="sender@example.com",
            to="recipient@example.com",
            subject="Test",
            text="Message",
        )

        assert "error" in result
        assert result["error"]["type"] == "configuration_error"

    @pytest.mark.asyncio
    async def test_send_message_with_html(self, monkeypatch):
        """Test send_message with HTML content."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"id": "123", "message": "Queued"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Plain text",
                html="<p>HTML</p>",
            )

            assert "id" in result
            assert result["id"] == "123"

    @pytest.mark.asyncio
    async def test_send_message_with_cc_bcc(self, monkeypatch):
        """Test send_message with CC and BCC."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"id": "456"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ) as mock_req:
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Message",
                cc="cc@example.com",
                bcc="bcc@example.com",
            )

            assert "id" in result
            # Verify the request was made with correct data
            call_args = mock_req.call_args
            assert call_args[1]["data"]["cc"] == "cc@example.com"
            assert call_args[1]["data"]["bcc"] == "bcc@example.com"

    @pytest.mark.asyncio
    async def test_send_message_with_attachment(self, monkeypatch):
        """Test send_message with attachment."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"id": "789"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ) as mock_req:
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test with attachment",
                text="Message",
                attachment="/path/to/file.pdf",
            )

            assert "id" in result
            call_args = mock_req.call_args
            assert call_args[1]["data"]["attachment"] == "/path/to/file.pdf"

    @pytest.mark.asyncio
    async def test_send_message_with_tag(self, monkeypatch):
        """Test send_message with custom tag."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"id": "101"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ) as mock_req:
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Message",
                tag="campaign1",
            )

            assert "id" in result
            call_args = mock_req.call_args
            assert call_args[1]["data"]["o:tag"] == "campaign1"

    @pytest.mark.asyncio
    async def test_send_message_with_schedule(self, monkeypatch):
        """Test send_message with scheduled delivery."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"id": "202"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ) as mock_req:
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Message",
                schedule_at="2024-01-01 12:00:00",
            )

            assert "id" in result
            call_args = mock_req.call_args
            assert call_args[1]["data"]["o:schedule"] == "2024-01-01 12:00:00"

    @pytest.mark.asyncio
    async def test_send_message_mailgun_error(self, monkeypatch):
        """Test send_message handles Mailgun API errors."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Message",
            )

            assert "error" in result
            assert result["error"]["type"] == "mailgun_error"
            assert result["error"]["message"].startswith("Mailgun request failed")

    @pytest.mark.asyncio
    async def test_send_message_success_response(self, monkeypatch):
        """Test send_message with successful response (200-299)."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = MagicMock()
        mock_response.is_success = False  # But status_code is 200
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"id": "200-test", "message": "OK"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Message",
            )

            assert "id" in result
            assert result["id"] == "200-test"


class TestDomains:
    """Test domain management functions."""

    @pytest.mark.asyncio
    async def test_get_domains_success(self, monkeypatch):
        """Test get_domains returns domain list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"items": [{"name": "example.com", "state": "active"}]}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_domains(limit=10, skip=0)
            assert "items" in result
            assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_get_domain_success(self, monkeypatch):
        """Test get_domain returns specific domain."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"domain": {"name": "example.com", "smtp_password": "xxx"}}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_domain("example.com")
            assert "domain" in result

    @pytest.mark.asyncio
    async def test_create_domain_success(self, monkeypatch):
        """Test create_domain creates new domain."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"domain": {"name": "newdomain.com"}}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await create_domain("newdomain.com", "password123")
            assert "domain" in result

    @pytest.mark.asyncio
    async def test_create_domain_with_options(self, monkeypatch):
        """Test create_domain with all options."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"domain": {"name": "newdomain.com"}}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ) as mock_req:
            result = await create_domain(
                domain_name="newdomain.com",
                smtp_password="pass",
                spam_action="tag",
                wildcard=True,
                ips="1.2.3.4",
                pool_id="pool1",
            )

            assert "domain" in result
            call_args = mock_req.call_args
            data = call_args[1]["data"]
            assert data["spam_action"] == "tag"
            assert data["wildcard"] == "true"

    @pytest.mark.asyncio
    async def test_delete_domain_success(self, monkeypatch):
        """Test delete_domain removes domain."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Domain deleted"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await delete_domain("example.com")
            assert "message" in result

    @pytest.mark.asyncio
    async def test_verify_domain_success(self, monkeypatch):
        """Test verify_domain triggers verification."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"domain": {"name": "example.com", "state": "verified"}}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await verify_domain("example.com")
            assert "domain" in result

    @pytest.mark.asyncio
    async def test_verify_domain_error(self, monkeypatch):
        """Test verify_domain handles errors."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 404
        mock_response.text = "Not found"

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await verify_domain("example.com")
            assert "error" in result


class TestEventsAndStats:
    """Test events and statistics functions."""

    @pytest.mark.asyncio
    async def test_get_events_success(self, monkeypatch):
        """Test get_events returns event list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"items": [{"event": "delivered"}]})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_events("example.com", event="delivered")
            assert "items" in result

    @pytest.mark.asyncio
    async def test_get_events_with_filters(self, monkeypatch):
        """Test get_events with time filters."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"items": []})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ) as mock_req:
            await get_events(
                domain_name="example.com",
                event="opened",
                begin="2024-01-01",
                end="2024-01-31",
                ascending="yes",
                limit=50,
            )

            call_args = mock_req.call_args
            params = call_args[1]["params"]
            assert params["event"] == "opened"
            assert params["begin"] == "2024-01-01"
            assert params["end"] == "2024-01-31"

    @pytest.mark.asyncio
    async def test_get_stats_success(self, monkeypatch):
        """Test get_stats returns statistics."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"stats": [{"delivered": 100}]})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_stats("example.com", ["delivered"], "2024-01-01")
            assert "stats" in result


class TestBounces:
    """Test bounce management functions."""

    @pytest.mark.asyncio
    async def test_get_bounces_success(self, monkeypatch):
        """Test get_bounces returns bounce list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"items": [{"address": "bounce@example.com"}]}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_bounces("example.com")
            assert "items" in result

    @pytest.mark.asyncio
    async def test_add_bounce_success(self, monkeypatch):
        """Test add_bounce adds to bounce list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Bounce added"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await add_bounce(
                "example.com", "bounce@example.com", code=550, error="User unknown"
            )
            assert "message" in result

    @pytest.mark.asyncio
    async def test_delete_bounce_success(self, monkeypatch):
        """Test delete_bounce removes from bounce list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Bounce deleted"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await delete_bounce("example.com", "bounce@example.com")
            assert "message" in result


class TestComplaints:
    """Test complaint management functions."""

    @pytest.mark.asyncio
    async def test_get_complaints_success(self, monkeypatch):
        """Test get_complaints returns complaint list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"items": [{"address": "complainant@example.com"}]}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_complaints("example.com")
            assert "items" in result

    @pytest.mark.asyncio
    async def test_add_complaint_success(self, monkeypatch):
        """Test add_complaint adds to complaint list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Complaint added"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await add_complaint("example.com", "complainant@example.com")
            assert "message" in result

    @pytest.mark.asyncio
    async def test_delete_complaint_success(self, monkeypatch):
        """Test delete_complaint removes from complaint list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Complaint deleted"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await delete_complaint("example.com", "complainant@example.com")
            assert "message" in result


class TestUnsubscribes:
    """Test unsubscribe management functions."""

    @pytest.mark.asyncio
    async def test_get_unsubscribes_success(self, monkeypatch):
        """Test get_unsubscribes returns unsubscribe list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"items": [{"address": "unsub@example.com"}]}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_unsubscribes("example.com")
            assert "items" in result

    @pytest.mark.asyncio
    async def test_add_unsubscribe_success(self, monkeypatch):
        """Test add_unsubscribe adds to unsubscribe list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Unsubscribe added"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await add_unsubscribe(
                "example.com", "unsub@example.com", tag="newsletter"
            )
            assert "message" in result

    @pytest.mark.asyncio
    async def test_delete_unsubscribe_success(self, monkeypatch):
        """Test delete_unsubscribe removes from unsubscribe list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Unsubscribe deleted"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await delete_unsubscribe("example.com", "unsub@example.com")
            assert "message" in result


class TestRoutes:
    """Test route management functions."""

    @pytest.mark.asyncio
    async def test_get_routes_success(self, monkeypatch):
        """Test get_routes returns route list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"items": [{"id": "route1", "priority": 0}]}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_routes()
            assert "items" in result

    @pytest.mark.asyncio
    async def test_get_route_success(self, monkeypatch):
        """Test get_route returns specific route."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"route": {"id": "route1"}})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_route("route1")
            assert "route" in result

    @pytest.mark.asyncio
    async def test_create_route_success(self, monkeypatch):
        """Test create_route creates new route."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"route": {"id": "route2"}})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await create_route(
                priority=0,
                expression="match_recipient('.*@example.com')",
                action=["forward('http://example.com')"],
            )
            assert "route" in result

    @pytest.mark.asyncio
    async def test_update_route_success(self, monkeypatch):
        """Test update_route modifies existing route."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"route": {"id": "route1"}})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await update_route("route1", priority=1)
            assert "route" in result

    @pytest.mark.asyncio
    async def test_update_route_all_fields(self, monkeypatch):
        """Test update_route with all optional fields."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"route": {"id": "route1"}})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await update_route(
                route_id="route1",
                priority=2,
                expression="match_recipient('.*@test.com')",
                action=["forward('http://test.com')"],
                description="Updated route",
            )
            assert "route" in result

    @pytest.mark.asyncio
    async def test_delete_route_success(self, monkeypatch):
        """Test delete_route removes route."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Route deleted"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await delete_route("route1")
            assert "message" in result


class TestTemplates:
    """Test template management functions."""

    @pytest.mark.asyncio
    async def test_get_templates_success(self, monkeypatch):
        """Test get_templates returns template list."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"items": [{"name": "template1"}]})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_templates()
            assert "items" in result

    @pytest.mark.asyncio
    async def test_get_template_success(self, monkeypatch):
        """Test get_template returns specific template."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"template": {"name": "template1"}})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_template("template1")
            assert "template" in result

    @pytest.mark.asyncio
    async def test_create_template_success(self, monkeypatch):
        """Test create_template creates new template."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"template": {"name": "newtemplate"}}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await create_template(
                name="newtemplate",
                subject="Test Subject",
                template_text="Hello {{name}}",
                template_html="<p>Hello {{name}}</p>",
            )
            assert "template" in result

    @pytest.mark.asyncio
    async def test_update_template_success(self, monkeypatch):
        """Test update_template modifies existing template."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"template": {"name": "template1"}})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await update_template(
                "template1", description="Updated description"
            )
            assert "template" in result

    @pytest.mark.asyncio
    async def test_update_template_all_fields(self, monkeypatch):
        """Test update_template with all optional fields."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"template": {"name": "template1"}})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await update_template(
                template_name="template1",
                description="Full update",
                template_version_name="v2",
                template_version_subject="New Subject",
                template_version_template="New content",
                template_version_html="<p>New HTML</p>",
                template_version_active=True,
            )
            assert "template" in result

    @pytest.mark.asyncio
    async def test_delete_template_success(self, monkeypatch):
        """Test delete_template removes template."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Template deleted"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await delete_template("template1")
            assert "message" in result


class TestWebhooks:
    """Test webhook management functions."""

    @pytest.mark.asyncio
    async def test_get_webhooks_success(self, monkeypatch):
        """Test get_webhooks returns all webhooks."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"webhooks": {"opened": {"url": "http://example.com"}}}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_webhooks()
            assert "webhooks" in result

    @pytest.mark.asyncio
    async def test_get_webhook_success(self, monkeypatch):
        """Test get_webhook returns specific webhook."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"webhook": {"url": "http://example.com"}}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await get_webhook("opened")
            assert "webhook" in result

    @pytest.mark.asyncio
    async def test_create_webhook_success(self, monkeypatch):
        """Test create_webhook creates new webhook."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(
            return_value={"webhook": {"url": "http://newexample.com"}}
        )

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await create_webhook("opened", "http://newexample.com")
            assert "webhook" in result

    @pytest.mark.asyncio
    async def test_delete_webhook_success(self, monkeypatch):
        """Test delete_webhook removes webhook."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"message": "Webhook deleted"})

        with patch(
            "mailgun_mcp.main._http_request", new=AsyncMock(return_value=mock_response)
        ):
            result = await delete_webhook("opened")
            assert "message" in result


class TestHTTPRequest:
    """Test _http_request helper function."""

    @pytest.mark.asyncio
    async def test_http_request_get(self):
        """Test _http_request with GET method."""
        mock_response = MagicMock()
        mock_response.is_success = True

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            result = await _http_request("GET", "http://example.com")
            assert result.is_success

    @pytest.mark.asyncio
    async def test_http_request_post(self):
        """Test _http_request with POST method."""
        mock_response = MagicMock()
        mock_response.is_success = True

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)):
            result = await _http_request(
                "POST", "http://example.com", data={"key": "value"}
            )
            assert result.is_success

    @pytest.mark.asyncio
    async def test_http_request_put(self):
        """Test _http_request with PUT method."""
        mock_response = MagicMock()
        mock_response.is_success = True

        with patch("httpx.AsyncClient.put", new=AsyncMock(return_value=mock_response)):
            result = await _http_request(
                "PUT", "http://example.com", data={"key": "value"}
            )
            assert result.is_success

    @pytest.mark.asyncio
    async def test_http_request_delete(self):
        """Test _http_request with DELETE method."""
        mock_response = MagicMock()
        mock_response.is_success = True

        with patch(
            "httpx.AsyncClient.delete", new=AsyncMock(return_value=mock_response)
        ):
            result = await _http_request("DELETE", "http://example.com")
            assert result.is_success
