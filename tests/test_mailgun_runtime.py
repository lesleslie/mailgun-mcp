"""Runtime integration test for Mailgun MCP Server.

This test verifies the Oneiric runtime integration is working correctly.
Tests import paths, configuration loading, and basic lifecycle operations.
"""

import pytest


# Test 1: Verify Oneiric modules can be imported
def test_oneiric_imports():
    """Test that Oneiric runtime modules are accessible."""
    # Core CLI imports
    from oneiric.core.cli import MCPServerCLIFactory
    from oneiric.core.config import OneiricMCPConfig

    # Runtime imports
    from oneiric.runtime.snapshot import RuntimeSnapshotManager
    from oneiric.runtime.cache import RuntimeCacheManager
    from oneiric.runtime.mcp_health import HealthCheckResponse, HealthStatus, HealthMonitor

    # Verify classes exist
    assert MCPServerCLIFactory is not None
    assert OneiricMCPConfig is not None
    assert RuntimeSnapshotManager is not None
    assert RuntimeCacheManager is not None
    assert HealthMonitor is not None
    assert HealthStatus is not None
    assert HealthCheckResponse is not None


# Test 2: Verify MailgunConfig configuration class
def test_mailgun_config():
    """Test that MailgunConfig can be instantiated."""
    from mailgun_mcp.__main__ import MailgunConfig

    # Create configuration with defaults
    config = MailgunConfig()

    # Verify default values
    assert config.http_port == 3039
    assert config.http_host == "127.0.0.1"
    assert config.enable_http_transport is True
    assert config.cache_dir is None or config.cache_dir == ".oneiric_cache"


# Test 3: Verify MailgunMCPServer can be created
def test_mailgun_server_creation():
    """Test that MailgunMCPServer can be instantiated."""
    from mailgun_mcp.__main__ import MailgunConfig, MailgunMCPServer

    # Create configuration
    config = MailgunConfig()

    # Create server instance
    server = MailgunMCPServer(config)

    # Verify runtime components are initialized
    assert server.config is not None
    assert server.snapshot_manager is not None
    assert server.cache_manager is not None
    assert server.health_monitor is not None
    assert server.mcp is not None


# Test 4: Verify health check can be executed
@pytest.mark.asyncio
async def test_mailgun_health_check():
    """Test that health check method works."""
    from mailgun_mcp.__main__ import MailgunConfig, MailgunMCPServer

    # Create server
    config = MailgunConfig()
    server = MailgunMCPServer(config)

    # Execute health check
    health_response = await server.health_check()

    # Verify response structure
    assert health_response is not None
    assert hasattr(health_response, 'status')
    assert hasattr(health_response, 'components')
    assert len(health_response.components) > 0


# Test 5: Verify cache directory can be configured
def test_cache_directory_configuration():
    """Test that custom cache directory can be set."""
    from mailgun_mcp.__main__ import MailgunConfig

    # Create config with custom cache dir
    config = MailgunConfig(cache_dir="/tmp/test_cache")

    # Verify cache directory is set
    assert config.cache_dir == "/tmp/test_cache"


# Test 6: Verify CLI factory can be created
def test_cli_factory_creation():
    """Test that MCPServerCLIFactory can be created for Mailgun."""
    from oneiric.core.cli import MCPServerCLIFactory
    from mailgun_mcp.__main__ import MailgunConfig, MailgunMCPServer

    # Create CLI factory
    cli_factory = MCPServerCLIFactory(
        server_class=MailgunMCPServer,
        config_class=MailgunConfig,
        name="mailgun-mcp",
        use_subcommands=True,
        legacy_flags=False,
        description="Mailgun MCP Server - Email management via Mailgun API"
    )

    # Verify factory configuration
    assert cli_factory.server_class == MailgunMCPServer
    assert cli_factory.config_class == MailgunConfig
    assert cli_factory.name == "mailgun-mcp"
    assert cli_factory.use_subcommands is True
    assert cli_factory.legacy_flags is False


# Test 7: Verify environment prefix configuration
def test_environment_prefix():
    """Test that environment variable prefix is correctly configured."""
    from mailgun_mcp.__main__ import MailgunConfig

    # Check Config class attributes
    assert hasattr(MailgunConfig.Config, 'env_prefix')
    assert MailgunConfig.Config.env_prefix == "MAILGUN_MCP_"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
