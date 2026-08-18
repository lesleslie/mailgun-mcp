"""Tool profile registration groups for mailgun-mcp MCP server.

Maps ``ToolProfile`` levels to specific ``register_<group>_tools()`` call
lists, controlling which tools are exposed at startup based on the
``MAILGUN_TOOL_PROFILE`` environment variable.

Profile tiers:
    MINIMAL:  No tools registered (only ``discover_tools`` meta-tool + /healthz route).
    STANDARD: Daily-driver tools — sending, stats, events, domains, routes,
              templates (18 tools).
    FULL:     All groups including suppression (bounces/complaints/
              unsubscribes) and webhook management (31 tools total).

The dispatch surface (``PROFILE_REGISTRATIONS`` + ``REGISTRATION_MAP`` +
``register_all_tool_groups``) is consumed by
``mailgun_mcp.main.apply_mailgun_tool_profile`` which delegates to
``mcp_common.tools.dispatch._apply_tool_profile``.

W2b.1 migration: replaces the inline ``@mcp.tool(...)`` decorator mode (which
registered all 31 tools at module import) with a callable-mode architecture.
The 31 decorator registrations became 8 ``register_<group>_tools(server)``
functions dispatched by the W0 helper.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_common.tools import ToolProfile
from mcp_common.tools.dispatch import ALL_TOOLS

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastmcp import FastMCP

MINIMAL_REGISTRATIONS: list[str | Callable[[FastMCP], Awaitable[None] | None]] = []

STANDARD_REGISTRATIONS: list[str | Callable[[FastMCP], Awaitable[None] | None]] = [
    "send_tools",
    "stats_tools",
    "events_tools",
    "domain_tools",
    "routes_tools",
    "templates_tools",
]

FULL_REGISTRATIONS: list[str | Callable[[FastMCP], Awaitable[None] | None]] = [
    *STANDARD_REGISTRATIONS,
    "suppression_tools",
    "webhook_tools",
]

PROFILE_REGISTRATIONS: dict[
    ToolProfile,
    list[str | Callable[[FastMCP], Awaitable[None] | None]] | type[ALL_TOOLS],
] = {
    ToolProfile.MINIMAL: MINIMAL_REGISTRATIONS,
    ToolProfile.STANDARD: STANDARD_REGISTRATIONS,
    ToolProfile.FULL: FULL_REGISTRATIONS,
}


# ---------------------------------------------------------------------------
# W0 apply_tool_profile dispatch surface.
#
# REGISTRATION_MAP routes each group key from PROFILE_REGISTRATIONS to a
# per-group registration callable (taking the FastMCP app). Lazy import keeps
# this module importable without forcing main.py to fully evaluate the 8
# register_*() functions at import time.
# ---------------------------------------------------------------------------
def _build_registration_map() -> dict[str, Callable[[FastMCP], Awaitable[None] | None]]:
    """Build the {group_key: register_fn(app)} map.

    Local import keeps ``mailgun_mcp.tools.profiles`` importable without
    forcing every register_X_tools function in ``mailgun_mcp.main`` to be
    resolved at module import time. Called by
    ``mailgun_mcp.main.apply_mailgun_tool_profile`` (not eagerly at import)
    because main.py imports this one at module load.
    """
    from mailgun_mcp.main import (
        register_domain_tools,
        register_events_tools,
        register_routes_tools,
        register_send_tools,
        register_stats_tools,
        register_suppression_tools,
        register_templates_tools,
        register_webhook_tools,
    )

    return {
        "send_tools": register_send_tools,
        "stats_tools": register_stats_tools,
        "events_tools": register_events_tools,
        "domain_tools": register_domain_tools,
        "routes_tools": register_routes_tools,
        "templates_tools": register_templates_tools,
        "suppression_tools": register_suppression_tools,
        "webhook_tools": register_webhook_tools,
    }


def register_all_tool_groups(server: FastMCP) -> None:
    """Bulk register every mailgun-mcp tool group (called at FULL profile).

    Used as ``register_all_fn`` for the W0 helper. Imports each
    register_<group>_tools directly (not via REGISTRATION_MAP iteration) so
    that adding a new group requires editing both this function and the
    FULL_REGISTRATIONS list — the redundancy is intentional: each is the
    ground-truth for a separate concern.
    """
    from mailgun_mcp.main import (
        register_domain_tools,
        register_events_tools,
        register_routes_tools,
        register_send_tools,
        register_stats_tools,
        register_suppression_tools,
        register_templates_tools,
        register_webhook_tools,
    )

    register_send_tools(server)
    register_stats_tools(server)
    register_events_tools(server)
    register_domain_tools(server)
    register_routes_tools(server)
    register_templates_tools(server)
    register_suppression_tools(server)
    register_webhook_tools(server)


__all__ = [
    "FULL_REGISTRATIONS",
    "MINIMAL_REGISTRATIONS",
    "PROFILE_REGISTRATIONS",
    "STANDARD_REGISTRATIONS",
    "_build_registration_map",
    "register_all_tool_groups",
]
