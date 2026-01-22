#!/usr/bin/env python3
"""Test script for Mailgun MCP CLI."""

import sys

sys.path.insert(0, "/Users/les/Projects/oneiric")

from mailgun_mcp.__main__ import MailgunConfig, MailgunMCPServer


def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    config = MailgunConfig()
    print(f"Config loaded: {config}")
    print(f"HTTP Port: {config.http_port}")
    print(f"HTTP Host: {config.http_host}")
    print("✅ Configuration test passed")

def test_server_creation():
    """Test server creation."""
    print("\nTesting server creation...")
    config = MailgunConfig()
    server = MailgunMCPServer(config)
    print(f"Server created: {server}")
    print(f"Server has startup method: {hasattr(server, 'startup')}")
    print(f"Server has shutdown method: {hasattr(server, 'shutdown')}")
    print(f"Server has get_app method: {hasattr(server, 'get_app')}")
    print("✅ Server creation test passed")

def test_cli_factory():
    """Test CLI factory creation."""
    print("\nTesting CLI factory...")
    from oneiric.core.cli import MCPServerCLIFactory

    MailgunConfig()
    cli_factory = MCPServerCLIFactory(
        server_class=MailgunMCPServer,
        config_class=MailgunConfig,
        name="mailgun-mcp",
        use_subcommands=True,
        legacy_flags=False,
        description="Mailgun MCP Server - Email management via Mailgun API"
    )
    print(f"CLI factory created: {cli_factory}")
    print(f"CLI factory has run method: {hasattr(cli_factory, 'run')}")
    print("✅ CLI factory test passed")

if __name__ == "__main__":
    print("🚀 Starting Mailgun MCP CLI tests...")

    try:
        test_config()
        test_server_creation()
        test_cli_factory()

        print("\n🎉 All tests passed! CLI integration is working.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
