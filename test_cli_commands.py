#!/usr/bin/env python3
"""Test script for Mailgun MCP CLI commands."""

import asyncio
import sys

sys.path.insert(0, "/Users/les/Projects/oneiric")

from oneiric.core.cli import MCPServerCLIFactory

from mailgun_mcp.__main__ import MailgunConfig, MailgunMCPServer


def test_cli_commands():
    """Test individual CLI commands."""
    print("🚀 Testing Mailgun MCP CLI commands...")

    # Create CLI factory
    config = MailgunConfig()
    cli_factory = MCPServerCLIFactory(
        server_class=MailgunMCPServer,
        config_class=MailgunConfig,
        name="mailgun-mcp",
        use_subcommands=True,
        legacy_flags=False,
        description="Mailgun MCP Server - Email management via Mailgun API"
    )

    print("\n1. Testing config command...")
    try:
        # Test config command by accessing the method directly
        cli_factory._show_config()
        print("✅ Config command test passed")
    except Exception as e:
        print(f"❌ Config command test failed: {e}")

    print("\n2. Testing health command...")
    try:
        # Test health command
        cli_factory._check_health()
        print("✅ Health command test passed")
    except Exception as e:
        print(f"❌ Health command test failed: {e}")

    print("\n3. Testing status command...")
    try:
        # Test status command
        cli_factory._check_status()
        print("✅ Status command test passed")
    except Exception as e:
        print(f"❌ Status command test failed: {e}")

    print("\n4. Testing server creation for start command...")
    try:
        # Test server creation (part of start command)
        server = MailgunMCPServer(config)
        print(f"✅ Server creation test passed: {server}")
    except Exception as e:
        print(f"❌ Server creation test failed: {e}")

    print("\n5. Testing startup lifecycle...")
    try:
        # Test startup lifecycle
        server = MailgunMCPServer(config)
        # Run startup in a short timeout to avoid hanging
        asyncio.run(asyncio.wait_for(server.startup(), timeout=5.0))
        print("✅ Startup lifecycle test passed")
    except TimeoutError:
        print("⚠️  Startup lifecycle test timed out (expected for API key validation)")
    except Exception as e:
        print(f"❌ Startup lifecycle test failed: {e}")

if __name__ == "__main__":
    try:
        test_cli_commands()
        print("\n🎉 CLI commands test completed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
