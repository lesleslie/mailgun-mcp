#!/usr/bin/env python3

import asyncio
from unittest.mock import patch

from mailgun_mcp.main import _get_requests_adapter, send_message
from tests.test_main import AsyncMock


async def debug_test():
    # Mock the environment variables
    import os

    os.environ["MAILGUN_API_KEY"] = "test-key"
    os.environ["MAILGUN_DOMAIN"] = "example.com"

    # Create a mock response using AsyncMock (as in original test)

    mock_response = AsyncMock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "sent", "id": "msg123"}

    # Check what _get_requests_adapter returns
    adapter = _get_requests_adapter()
    print(f"_get_requests_adapter returns: {adapter}")

    # Mock the httpx AsyncClient context manager and its post method
    with patch("mailgun_mcp.main.httpx.AsyncClient") as MockAsyncClient:
        # Configure the mock to properly handle the async context manager protocol
        mock_client_instance = AsyncMock()
        # Since we now call the specific method (post), set that up
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

        print(f"Result type: {type(result)}")
        print(f"Result dir: {dir(result)}")

        # Check various attributes of ToolResult
        if hasattr(result, "structured_content"):
            print(f"Structured content: {result.structured_content}")
        if hasattr(result, "__dict__"):
            print(f"Object attributes: {result.__dict__}")
        if hasattr(result, "value"):
            print(f"Value: {result.value}")
        if hasattr(result, "result"):
            print(f"Result: {result.result}")

        # Check if result is awaitable itself
        import inspect

        if inspect.isawaitable(result):
            print("Result is awaitable")

        print(f"MockAsyncClient calls: {MockAsyncClient.call_count}")
        print(f"Mock client instance calls: {mock_client_instance.method_calls}")
        print(f"Request call args: {mock_client_instance.request.call_args}")


if __name__ == "__main__":
    asyncio.run(debug_test())
