"""
Test suite for email sending functionality with comprehensive coverage.

Tests email sending with various configurations, attachments, error handling,
and edge cases. All Mailgun API calls are mocked.
"""

import os
import tempfile
from unittest.mock import AsyncMock, patch

import pytest

from mailgun_mcp.main import (
    MAX_ATTACHMENT_SIZE,
    send_message,
)


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("MAILGUN_API_KEY", "test-api-key-12345678")
    monkeypatch.setenv("MAILGUN_DOMAIN", "test.example.com")
    return monkeypatch


@pytest.fixture
def mock_httpx_response():
    """Create a mock successful httpx response."""
    response = AsyncMock()
    response.is_success = True
    response.status_code = 200
    response.json.return_value = {
        "id": "<message-id@test.example.com>",
        "message": "Queued. Thank you.",
    }
    response.text = "Queued. Thank you."
    return response


@pytest.fixture
def mock_httpx_error_response():
    """Create a mock error httpx response."""
    response = AsyncMock()
    response.is_success = False
    response.status_code = 400
    response.text = "Invalid parameters"
    response.json.return_value = {"message": "Bad request"}
    return response


class TestEmailSending:
    """Test email sending functionality."""

    @pytest.mark.asyncio
    async def test_send_simple_email(self, mock_env, mock_httpx_response):
        """Test sending a simple text email."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Test Subject",
                text="Test message body",
            )

            assert result["id"] == "<message-id@test.example.com>"
            assert result["message"] == "Queued. Thank you."
            instance.post.assert_called_once()

            # Verify the call was made with correct parameters
            call_args = instance.post.call_args
            assert "api.mailgun.net" in call_args[0][0]
            assert call_args[1]["data"]["from"] == "sender@test.example.com"
            assert call_args[1]["data"]["to"] == "recipient@example.com"
            assert call_args[1]["data"]["subject"] == "Test Subject"
            assert call_args[1]["data"]["text"] == "Test message body"

    @pytest.mark.asyncio
    async def test_send_email_with_cc_bcc(self, mock_env, mock_httpx_response):
        """Test sending email with CC and BCC recipients."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Test with CC/BCC",
                text="Test body",
                cc="cc@example.com",
                bcc="bcc@example.com",
            )

            assert result["id"] == "<message-id@test.example.com>"

            call_args = instance.post.call_args
            assert call_args[1]["data"]["cc"] == "cc@example.com"
            assert call_args[1]["data"]["bcc"] == "bcc@example.com"

    @pytest.mark.asyncio
    async def test_send_html_email(self, mock_env, mock_httpx_response):
        """Test sending email with HTML content."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            html_content = "<html><body><h1>Hello</h1><p>This is HTML</p></body></html>"

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="HTML Email",
                text="Plain text version",
                html=html_content,
            )

            assert result["id"] == "<message-id@test.example.com>"

            call_args = instance.post.call_args
            assert call_args[1]["data"]["html"] == html_content

    @pytest.mark.asyncio
    async def test_send_email_with_tag(self, mock_env, mock_httpx_response):
        """Test sending email with a tag for tracking."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Tagged Email",
                text="Test body",
                tag="campaign-2024",
            )

            assert result["id"] == "<message-id@test.example.com>"

            call_args = instance.post.call_args
            assert call_args[1]["data"]["o:tag"] == "campaign-2024"

    @pytest.mark.asyncio
    async def test_send_email_with_schedule(self, mock_env, mock_httpx_response):
        """Test sending scheduled email."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            schedule_time = "2024-12-31 23:59:59"

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Scheduled Email",
                text="Test body",
                schedule_at=schedule_time,
            )

            assert result["id"] == "<message-id@test.example.com>"

            call_args = instance.post.call_args
            assert call_args[1]["data"]["o:schedule"] == schedule_time

    @pytest.mark.asyncio
    async def test_send_email_with_all_options(self, mock_env, mock_httpx_response):
        """Test sending email with all optional parameters."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Complete Email",
                text="Plain text",
                cc="cc@example.com",
                bcc="bcc@example.com",
                html="<p>HTML version</p>",
                tag="full-test",
                schedule_at="2024-12-31 23:59:59",
            )

            assert result["id"] == "<message-id@test.example.com>"

            call_args = instance.post.call_args
            data = call_args[1]["data"]
            assert data["cc"] == "cc@example.com"
            assert data["bcc"] == "bcc@example.com"
            assert data["html"] == "<p>HTML version</p>"
            assert data["o:tag"] == "full-test"
            assert data["o:schedule"] == "2024-12-31 23:59:59"


class TestAttachmentHandling:
    """Test attachment handling and validation."""

    @pytest.mark.asyncio
    async def test_send_email_with_small_attachment(
        self, mock_env, mock_httpx_response
    ):
        """Test sending email with a small attachment."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as tmp_file:
            tmp_file.write("This is a small test attachment.")
            tmp_file_path = tmp_file.name

        try:
            with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
                instance = MockAsyncClient.return_value.__aenter__.return_value
                instance.post.return_value = mock_httpx_response

                result = await send_message(
                    from_email="sender@test.example.com",
                    to="recipient@example.com",
                    subject="Email with attachment",
                    text="Please find attached file.",
                    attachment=tmp_file_path,
                )

                assert result["id"] == "<message-id@test.example.com>"

                call_args = instance.post.call_args
                assert call_args[1]["data"]["attachment"] == tmp_file_path, (
                    "Attachment path should be included"
                )
        finally:
            # Clean up
            os.unlink(tmp_file_path)

    @pytest.mark.asyncio
    async def test_send_email_with_missing_attachment(self, mock_env):
        """Test sending email with non-existent attachment file."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Email with missing attachment",
                text="Test",
                attachment="/nonexistent/path/to/file.txt",
            )

            assert "error" in result
            assert result["error"]["type"] == "validation_error"
            assert "not found" in result["error"]["message"].lower()

            # Verify no HTTP call was made
            instance.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_email_with_oversized_attachment(self, mock_env):
        """Test sending email with attachment exceeding size limit."""
        # Create a temporary file larger than MAX_ATTACHMENT_SIZE
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".txt"
        ) as tmp_file:
            # Write more than MAX_ATTACHMENT_SIZE bytes
            tmp_file.write(b"x" * (MAX_ATTACHMENT_SIZE + 1))
            tmp_file_path = tmp_file.name

        try:
            with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
                instance = MockAsyncClient.return_value.__aenter__.return_value

                result = await send_message(
                    from_email="sender@test.example.com",
                    to="recipient@example.com",
                    subject="Email with large attachment",
                    text="Test",
                    attachment=tmp_file_path,
                )

                assert "error" in result
                assert result["error"]["type"] == "validation_error"
                assert "too large" in result["error"]["message"].lower()

                # Verify no HTTP call was made
                instance.post.assert_not_called()
        finally:
            # Clean up
            os.unlink(tmp_file_path)

    @pytest.mark.asyncio
    async def test_send_email_with_boundary_size_attachment(
        self, mock_env, mock_httpx_response
    ):
        """Test sending email with attachment exactly at the size limit."""
        # Create a temporary file exactly at MAX_ATTACHMENT_SIZE bytes
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".txt"
        ) as tmp_file:
            tmp_file.write(b"x" * MAX_ATTACHMENT_SIZE)
            tmp_file_path = tmp_file.name

        try:
            with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
                instance = MockAsyncClient.return_value.__aenter__.return_value
                instance.post.return_value = mock_httpx_response

                result = await send_message(
                    from_email="sender@test.example.com",
                    to="recipient@example.com",
                    subject="Email with max size attachment",
                    text="Test",
                    attachment=tmp_file_path,
                )

                assert result["id"] == "<message-id@test.example.com>"

                call_args = instance.post.call_args
                assert call_args[1]["data"]["attachment"] == tmp_file_path
        finally:
            # Clean up
            os.unlink(tmp_file_path)

    @pytest.mark.asyncio
    async def test_send_email_with_various_file_types(
        self, mock_env, mock_httpx_response
    ):
        """Test sending emails with various file types as attachments."""
        test_cases = [
            ("text.txt", b"Plain text content"),
            ("document.pdf", b"%PDF-1.4 fake pdf content"),
            ("image.jpg", b"\xff\xd8\xff\xe0 fake jpeg"),
            ("data.json", b'{"key": "value"}'),
        ]

        for filename, content in test_cases:
            with tempfile.NamedTemporaryFile(
                mode="wb", delete=False, suffix=os.path.splitext(filename)[1]
            ) as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name

            try:
                with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
                    instance = MockAsyncClient.return_value.__aenter__.return_value
                    instance.post.return_value = mock_httpx_response

                    result = await send_message(
                        from_email="sender@test.example.com",
                        to="recipient@example.com",
                        subject=f"Email with {filename}",
                        text="Test",
                        attachment=tmp_file_path,
                    )

                    assert result["id"] == "<message-id@test.example.com>"
                    assert (
                        instance.post.call_args[1]["data"]["attachment"]
                        == tmp_file_path
                    )
            finally:
                # Clean up
                os.unlink(tmp_file_path)

    @pytest.mark.asyncio
    async def test_send_email_with_binary_attachment(
        self, mock_env, mock_httpx_response
    ):
        """Test sending email with binary attachment."""
        # Create a binary file with various byte values
        binary_content = bytes(range(256)) * 10  # 2560 bytes

        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".bin"
        ) as tmp_file:
            tmp_file.write(binary_content)
            tmp_file_path = tmp_file.name

        try:
            with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
                instance = MockAsyncClient.return_value.__aenter__.return_value
                instance.post.return_value = mock_httpx_response

                result = await send_message(
                    from_email="sender@test.example.com",
                    to="recipient@example.com",
                    subject="Email with binary attachment",
                    text="Test",
                    attachment=tmp_file_path,
                )

                assert result["id"] == "<message-id@test.example.com>"
                assert instance.post.call_args[1]["data"]["attachment"] == tmp_file_path
        finally:
            # Clean up
            os.unlink(tmp_file_path)


class TestErrorHandling:
    """Test error handling for email sending."""

    @pytest.mark.asyncio
    async def test_send_without_api_key(self, monkeypatch):
        """Test sending email without API key configured."""
        # Remove API key from environment
        monkeypatch.delenv("MAILGUN_API_KEY", raising=False)
        monkeypatch.setenv("MAILGUN_DOMAIN", "test.example.com")

        result = await send_message(
            from_email="sender@test.example.com",
            to="recipient@example.com",
            subject="Test",
            text="Test",
        )

        assert "error" in result
        assert result["error"]["type"] == "configuration_error"
        assert "MAILGUN_API_KEY" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_send_without_domain(self, monkeypatch):
        """Test sending email without domain configured."""
        # Remove domain from environment
        monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
        monkeypatch.delenv("MAILGUN_DOMAIN", raising=False)

        result = await send_message(
            from_email="sender@test.example.com",
            to="recipient@example.com",
            subject="Test",
            text="Test",
        )

        assert "error" in result
        assert result["error"]["type"] == "configuration_error"
        assert "MAILGUN_DOMAIN" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_send_without_credentials(self, monkeypatch):
        """Test sending email without any credentials configured."""
        # Remove all credentials from environment
        monkeypatch.delenv("MAILGUN_API_KEY", raising=False)
        monkeypatch.delenv("MAILGUN_DOMAIN", raising=False)

        result = await send_message(
            from_email="sender@test.example.com",
            to="recipient@example.com",
            subject="Test",
            text="Test",
        )

        assert "error" in result
        assert result["error"]["type"] == "configuration_error"
        assert "MAILGUN_API_KEY and MAILGUN_DOMAIN" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_send_with_mailgun_api_error(
        self, mock_env, mock_httpx_error_response
    ):
        """Test handling of Mailgun API errors."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_error_response

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
            )

            assert "error" in result
            assert result["error"]["type"] == "mailgun_error"
            assert "400" in result["error"]["message"]
            assert result["error"]["details"] == "Invalid parameters"

    @pytest.mark.asyncio
    async def test_send_with_network_error(self, mock_env):
        """Test handling of network errors."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            # Simulate network error
            instance.post.side_effect = Exception("Network error")

            with pytest.raises(Exception, match="Network error"):
                await send_message(
                    from_email="sender@test.example.com",
                    to="recipient@example.com",
                    subject="Test",
                    text="Test",
                )

    @pytest.mark.asyncio
    async def test_send_with_timeout_error(self, mock_env):
        """Test handling of timeout errors."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            # Simulate timeout
            import httpx2 as httpx

            instance.post.side_effect = httpx.TimeoutException(
                "Request timed out", request=None
            )

            with pytest.raises(httpx.TimeoutException):
                await send_message(
                    from_email="sender@test.example.com",
                    to="recipient@example.com",
                    subject="Test",
                    text="Test",
                )

    @pytest.mark.asyncio
    async def test_send_with_invalid_api_key(self, mock_env):
        """Test sending email with invalid API key (401 error)."""
        mock_response = AsyncMock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_response

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
            )

            assert "error" in result
            assert result["error"]["type"] == "mailgun_error"
            assert "401" in result["error"]["message"]
            assert result["error"]["details"] == "Invalid API key"


class TestAuthentication:
    """Test authentication and authorization."""

    @pytest.mark.asyncio
    async def test_auth_header_format(self, mock_env, mock_httpx_response):
        """Test that authentication is formatted correctly for Mailgun API."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
            )

            call_args = instance.post.call_args
            auth = call_args[1]["auth"]

            # Verify BasicAuth object
            assert hasattr(auth, "username")
            assert hasattr(auth, "password")
            assert auth.username == "api"
            assert auth.password == "test-api-key-12345678"

    @pytest.mark.asyncio
    async def test_uses_configured_api_key(self, mock_env, mock_httpx_response):
        """Test that the configured API key is used for authentication."""
        custom_api_key = "custom-api-key-99999999"
        mock_env.setenv("MAILGUN_API_KEY", custom_api_key)

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
            )

            call_args = instance.post.call_args
            auth = call_args[1]["auth"]

            assert auth.password == custom_api_key

    @pytest.mark.asyncio
    async def test_uses_configured_domain(self, mock_env, mock_httpx_response):
        """Test that the configured domain is used in the API endpoint."""
        custom_domain = "custom.example.org"
        mock_env.setenv("MAILGUN_DOMAIN", custom_domain)

        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Test",
                text="Test",
            )

            call_args = instance.post.call_args
            url = call_args[0][0]

            assert custom_domain in url
            assert f"v3/{custom_domain}/messages" in url


class TestEmailContentValidation:
    """Test email content validation and formatting."""

    @pytest.mark.asyncio
    async def test_send_with_empty_subject(self, mock_env, mock_httpx_response):
        """Test sending email with empty subject."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="",
                text="Test",
            )

            assert result["id"] == "<message-id@test.example.com>"

            call_args = instance.post.call_args
            assert call_args[1]["data"]["subject"] == ""

    @pytest.mark.asyncio
    async def test_send_with_unicode_content(self, mock_env, mock_httpx_response):
        """Test sending email with unicode characters."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Unicode Test: Hello, World! 🌍",
                text="Body with unicode: café, 日本語, emojis 😀",
            )

            assert result["id"] == "<message-id@test.example.com>"

            call_args = instance.post.call_args
            assert "🌍" in call_args[1]["data"]["subject"]
            assert "café" in call_args[1]["data"]["text"]
            assert "日本語" in call_args[1]["data"]["text"]
            assert "😀" in call_args[1]["data"]["text"]

    @pytest.mark.asyncio
    async def test_send_with_special_characters_in_subject(
        self, mock_env, mock_httpx_response
    ):
        """Test sending email with special characters in subject."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            special_subject = 'Test: [IMPORTANT] Re: Meeting @ 3pm - "Final" Review'
            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject=special_subject,
                text="Test",
            )

            assert result["id"] == "<message-id@test.example.com>"

            call_args = instance.post.call_args
            assert call_args[1]["data"]["subject"] == special_subject

    @pytest.mark.asyncio
    async def test_send_with_long_text_body(self, mock_env, mock_httpx_response):
        """Test sending email with very long text body."""
        with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
            instance = MockAsyncClient.return_value.__aenter__.return_value
            instance.post.return_value = mock_httpx_response

            long_text = "Line of text\n" * 1000  # ~14,000 characters

            result = await send_message(
                from_email="sender@test.example.com",
                to="recipient@example.com",
                subject="Long email",
                text=long_text,
            )

            assert result["id"] == "<message-id@test.example.com>"

            call_args = instance.post.call_args
            assert call_args[1]["data"]["text"] == long_text
