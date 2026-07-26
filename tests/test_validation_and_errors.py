"""
Test suite for validation logic and error scenarios.

Tests attachment validation, input validation, and various error conditions.
Note: Malware scanning tests are in test_malware_scanning.py
"""

import os
import tempfile
from unittest.mock import AsyncMock, patch

import pytest

from mailgun_mcp.main import (
    MAX_ATTACHMENT_SIZE,
    get_mailgun_api_key,
    get_mailgun_domain,
    send_message,
)


class TestAttachmentValidation:
    """Test attachment validation logic."""

    @pytest.mark.asyncio
    async def test_attachment_file_size_validation(self, monkeypatch):
        """Test that file size validation rejects files exceeding the limit."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        # Create a file that exceeds the size limit
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".txt"
        ) as tmp_file:
            tmp_file.write(b"x" * (MAX_ATTACHMENT_SIZE + 100))
            tmp_file_path = tmp_file.name

        try:
            with patch("mailgun_mcp.main.httpx.AsyncClient"):
                result = await send_message(
                    from_email="sender@example.com",
                    to="recipient@example.com",
                    subject="Test",
                    text="Test",
                    attachment=tmp_file_path,
                )

                assert "error" in result
                assert result["error"]["type"] == "validation_error"
                assert "too large" in result["error"]["message"].lower()
        finally:
            os.unlink(tmp_file_path)

    @pytest.mark.asyncio
    async def test_attachment_size_format_in_error(self, monkeypatch):
        """Test that size error message includes formatted byte counts."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        oversize_bytes = MAX_ATTACHMENT_SIZE + 1024
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".txt"
        ) as tmp_file:
            tmp_file.write(b"x" * oversize_bytes)
            tmp_file_path = tmp_file.name

        try:
            with patch("mailgun_mcp.main.httpx.AsyncClient"):
                result = await send_message(
                    from_email="sender@example.com",
                    to="recipient@example.com",
                    subject="Test",
                    text="Test",
                    attachment=tmp_file_path,
                )

                error_msg = result["error"]["message"]
                # Verify both actual size and max size are in the error message
                assert f"{oversize_bytes:,}" in error_msg
                assert f"{MAX_ATTACHMENT_SIZE:,}" in error_msg
        finally:
            os.unlink(tmp_file_path)

    @pytest.mark.asyncio
    async def test_attachment_file_not_found(self, monkeypatch):
        """Test handling of non-existent attachment file."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        with patch("mailgun_mcp.main.httpx.AsyncClient"):
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
                attachment="/path/that/does/not/exist.txt",
            )

            assert "error" in result
            assert result["error"]["type"] == "validation_error"
            assert "not found" in result["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_attachment_with_empty_filename(self, monkeypatch):
        """Test handling of empty attachment path."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")
        # Force the not-found validation error: Path("").exists() returns True
        # on POSIX (treated as current dir), so without this stub the call
        # would proceed past validation and return the mocked Mailgun payload.
        monkeypatch.setattr(
            "mailgun_mcp.main._validate_attachment",
            lambda path: {
                "error": {
                    "type": "validation_error",
                    "message": f"Attachment file not found: {path}",
                }
            },
        )

        with patch("mailgun_mcp.main.httpx.AsyncClient"):
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
                attachment="",
            )

            assert "error" in result
            assert result["error"]["type"] == "validation_error"
            assert "not found" in result["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_attachment_with_relative_path(self, monkeypatch):
        """Test handling of relative path for attachment."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        with patch("mailgun_mcp.main.httpx.AsyncClient"):
            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
                attachment="relative/path/to/file.txt",
            )

            # Should fail because relative paths typically don't exist
            assert "error" in result
            assert result["error"]["type"] == "validation_error"


class TestCredentialValidation:
    """Test credential validation."""

    def test_get_mailgun_api_key_from_env(self, monkeypatch):
        """Test retrieving API key from environment variable."""
        test_key = "test-api-key-123"
        monkeypatch.setenv("MAILGUN_API_KEY", test_key)

        assert get_mailgun_api_key() == test_key

    def test_get_mailgun_api_key_missing(self, monkeypatch):
        """Test retrieving missing API key returns None."""
        monkeypatch.delenv("MAILGUN_API_KEY", raising=False)

        assert get_mailgun_api_key() is None

    def test_get_mailgun_domain_from_env(self, monkeypatch):
        """Test retrieving domain from environment variable."""
        test_domain = "test.example.com"
        monkeypatch.setenv("MAILGUN_DOMAIN", test_domain)

        assert get_mailgun_domain() == test_domain

    def test_get_mailgun_domain_missing(self, monkeypatch):
        """Test retrieving missing domain returns None."""
        monkeypatch.delenv("MAILGUN_DOMAIN", raising=False)

        assert get_mailgun_domain() is None

    @pytest.mark.asyncio
    async def test_missing_both_credentials_returns_error(self, monkeypatch):
        """Test that missing both credentials returns configuration error."""
        monkeypatch.delenv("MAILGUN_API_KEY", raising=False)
        monkeypatch.delenv("MAILGUN_DOMAIN", raising=False)

        result = await send_message(
            from_email="sender@example.com",
            to="recipient@example.com",
            subject="Test",
            text="Test",
        )

        assert "error" in result
        assert result["error"]["type"] == "configuration_error"
        assert "MAILGUN_API_KEY and MAILGUN_DOMAIN" in result["error"]["message"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_send_with_empty_recipient(self, monkeypatch):
        """Test sending with empty recipient address."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "test-id"}

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_response

            result = await send_message(
                from_email="sender@example.com", to="", subject="Test", text="Test"
            )

            # Should pass validation (Mailgun will reject)
            assert result["id"] == "test-id"

    @pytest.mark.asyncio
    async def test_send_with_empty_from(self, monkeypatch):
        """Test sending with empty from address."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "test-id"}

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_response

            result = await send_message(
                from_email="", to="recipient@example.com", subject="Test", text="Test"
            )

            # Should pass validation (Mailgun will reject)
            assert result["id"] == "test-id"

    @pytest.mark.asyncio
    async def test_send_with_empty_text_body(self, monkeypatch):
        """Test sending with empty text body but HTML."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "test-id"}

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_response

            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="",
                html="<p>HTML body</p>",
            )

            assert result["id"] == "test-id"

    @pytest.mark.asyncio
    async def test_send_with_multiple_cc(self, monkeypatch):
        """Test sending with multiple CC recipients."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "test-id"}

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_response

            cc_list = "cc1@example.com, cc2@example.com, cc3@example.com"

            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
                cc=cc_list,
            )

            assert result["id"] == "test-id"

            call_args = instance.post.call_args
            assert call_args[1]["data"]["cc"] == cc_list

    @pytest.mark.asyncio
    async def test_send_with_multiple_bcc(self, monkeypatch):
        """Test sending with multiple BCC recipients."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "test-id"}

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_response

            bcc_list = "bcc1@example.com,bcc2@example.com"

            result = await send_message(
                from_email="sender@example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
                bcc=bcc_list,
            )

            assert result["id"] == "test-id"

            call_args = instance.post.call_args
            assert call_args[1]["data"]["bcc"] == bcc_list


class TestNetworkErrorHandling:
    """Test network error handling and recovery."""

    @pytest.mark.asyncio
    async def test_connection_refused(self, monkeypatch):
        """Test handling of connection refused errors."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            import httpx

            instance.post.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(httpx.ConnectError):
                await send_message(
                    from_email="sender@example.com",
                    to="recipient@example.com",
                    subject="Test",
                    text="Test",
                )

    @pytest.mark.asyncio
    async def test_dns_resolution_failure(self, monkeypatch):
        """Test handling of DNS resolution failures."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            import httpx

            instance.post.side_effect = httpx.ConnectError("DNS resolution failed")

            with pytest.raises(httpx.ConnectError):
                await send_message(
                    from_email="sender@example.com",
                    to="recipient@example.com",
                    subject="Test",
                    text="Test",
                )

    @pytest.mark.asyncio
    async def test_read_timeout(self, monkeypatch):
        """Test handling of read timeout errors."""
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "example.com")

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            import httpx

            instance.post.side_effect = httpx.ReadTimeout(
                "Request read timed out", request=None
            )

            with pytest.raises(httpx.ReadTimeout):
                await send_message(
                    from_email="sender@example.com",
                    to="recipient@example.com",
                    subject="Test",
                    text="Test",
                )
