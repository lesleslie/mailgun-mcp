"""Mailgun MCP Server."""

from __future__ import annotations

from importlib.metadata import version as _importlib_version

__version__ = _importlib_version("mailgun-mcp")

__all__ = ["__version__"]
