#!/usr/bin/env python3
"""Mailgun MCP Server - Oneiric CLI Entry Point."""

from typing import Any

from mcp_common.cli import MCPServerCLIFactory
from mcp_common.server import BaseOneiricServerMixin, create_runtime_components
from oneiric.core.config import OneiricMCPConfig
from oneiric.runtime.mcp_health import HealthStatus

# Import the main server from the existing codebase
from mailgun_mcp.main import mcp, validate_api_key_at_startup


class MailgunConfig(OneiricMCPConfig):
    """Mailgun MCP Server Configuration."""

    http_port: int = 3039
    http_host: str = "127.0.0.1"
    enable_http_transport: bool = True

    class Config:
        env_prefix = "MAILGUN_MCP_"
        env_file = ".env"


class MailgunMCPServer(BaseOneiricServerMixin):
    """Mailgun MCP Server with Oneiric integration."""

    def __init__(self, config: MailgunConfig):
        self.config = config
        self.mcp = mcp  # Use the existing FastMCP instance

        # Initialize runtime components using mcp-common helper
        self.runtime = create_runtime_components(
            server_name="mailgun-mcp", cache_dir=".oneiric_cache"
        )

        # Expose runtime components as convenience attributes
        self.snapshot_manager = self.runtime.snapshot_manager
        self.cache_manager = self.runtime.cache_manager
        self.health_monitor = self.runtime.health_monitor

    async def startup(self) -> None:
        """Server startup lifecycle hook."""
        # Validate API key at startup
        validate_api_key_at_startup()

        # Initialize runtime components
        await self.runtime.initialize()

        # Create startup snapshot with custom components
        await self._create_startup_snapshot(
            custom_components={
                "api_key": {
                    "status": "validated",
                    "timestamp": self._get_timestamp(),
                },
            }
        )

        print("✅ Mailgun MCP Server started successfully")
        print(f"   Listening on {self.config.http_host}:{self.config.http_port}")
        print(f"   Cache directory: {self.runtime.cache_dir}")

    async def shutdown(self) -> None:
        """Server shutdown lifecycle hook."""
        # Create shutdown snapshot
        await self._create_shutdown_snapshot()

        # Clean up runtime components
        await self.runtime.cleanup()

        print("👋 Mailgun MCP Server shutdown complete")

    async def health_check(self) -> dict[str, Any]:
        """Perform health check."""
        # Build base health components using mixin helper
        base_components = await self._build_health_components()

        # Add mailgun-specific health checks
        api_key_available = (
            bool(self.config.mailgun_api_key)
            if hasattr(self.config, "mailgun_api_key")
            else False
        )

        base_components.append(
            self.runtime.health_monitor.create_component_health(
                name="api_key",
                status=HealthStatus.HEALTHY
                if api_key_available
                else HealthStatus.UNHEALTHY,
                details={"configured": api_key_available},
            )
        )

        # Create health response
        return self.runtime.health_monitor.create_health_response(base_components)  # type: ignore

    def get_app(self) -> Any:  # Return type depends on mcp.http_app
        """Get the ASGI application."""
        return self.mcp.http_app

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        import time

        return time.strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    """Main entry point for Mailgun MCP Server."""

    # Create CLI factory using mcp-common's enhanced factory
    cli_factory = MCPServerCLIFactory.create_server_cli(
        server_class=MailgunMCPServer,
        config_class=MailgunConfig,
        name="mailgun-mcp",
    )

    # Create and run CLI
    cli_factory.create_app()()


if __name__ == "__main__":
    main()
