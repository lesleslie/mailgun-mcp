"""Test fixtures for mailgun-mcp test suite.

Provides a FastMCP 2.x compatibility shim for tests written against the 2.x
``FunctionTool`` API (``send_message.run({...})`` / ``send_message.name``).

In FastMCP 3.x, ``@mcp.tool()`` no longer replaces the decorated function
with a ``FunctionTool`` object — the function stays a function and tools are
fetched via ``await mcp.get_tool(name)``. This shim re-exposes each registered
tool as a callable wrapper that satisfies both invocation styles the tests
use:

* ``await tool.run(arguments)`` — 2.x style, returns a ``ToolResult`` with
  ``.structured_content`` set to the function's dict return.
* ``await tool(**kwargs)`` — direct call style used by
  ``test_validation_and_errors`` / ``test_email_sending`` (the wrapper
  delegates straight to the underlying function).

Because the tests use ``from mailgun_mcp.main import send_message`` and then
call ``send_message.run({...})`` on the local binding, the shim also walks
the test modules and rebinds the tool name on each of them — patching only
``mailgun_mcp.main`` would not affect imports already done at module load.
"""

from __future__ import annotations

import sys
from typing import Any

import pytest

import mailgun_mcp.main as _main


# Tool function names that the test suite imports from mailgun_mcp.main.
# Each one is a top-level async function decorated with ``@mcp.tool(...)``.
_TOOL_NAMES: tuple[str, ...] = (
    "send_message",
    "get_domains",
    "get_domain",
    "create_domain",
    "delete_domain",
    "verify_domain",
    "get_events",
    "get_stats",
    "get_bounces",
    "add_bounce",
    "delete_bounce",
    "get_complaints",
    "add_complaint",
    "delete_complaint",
    "get_unsubscribes",
    "add_unsubscribe",
    "delete_unsubscribe",
    "get_routes",
    "get_route",
    "create_route",
    "update_route",
    "delete_route",
    "get_templates",
    "get_template",
    "create_template",
    "update_template",
    "delete_template",
    "get_webhooks",
    "get_webhook",
    "create_webhook",
    "delete_webhook",
)


class _ToolWrapper:
    """FastMCP-2.x ``FunctionTool``-shaped adapter for a FastMCP-3.x tool function.

    The wrapper is the simplest thing that satisfies both call sites the
    tests use:

    * ``await wrapper.run(arguments)`` (the 73 ``AttributeError`` failures)
    * ``await wrapper(**kwargs)`` (the direct-call tests in
      ``test_validation_and_errors`` / ``test_email_sending``)
    """

    def __init__(self, name: str, fn: Any) -> None:
        self.name = name
        self._fn = fn

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self._fn(*args, **kwargs)

    async def run(self, arguments: dict[str, Any] | None = None) -> Any:
        """Invoke the underlying function and wrap the result.

        Returns a ``ToolResult``-like object exposing ``structured_content``
        so existing test assertions (``hasattr(result, "structured_content")``
        and ``result.structured_content``) keep working unchanged.
        """
        result = await self._fn(**(arguments or {}))

        # Lazy import to keep the shim resilient if FastMCP internals shift.
        from fastmcp.tools.base import ToolResult

        if isinstance(result, dict):
            return ToolResult(structured_content=result)
        return ToolResult(content=result)


def _build_wrappers() -> dict[str, _ToolWrapper]:
    """Build a name -> wrapper mapping once per process.

    Captures the original tool functions from the production module so the
    wrappers always delegate to the latest callable (even after monkeypatch
    replacements done elsewhere in the suite).
    """
    wrappers: dict[str, _ToolWrapper] = {}
    for name in _TOOL_NAMES:
        original = getattr(_main, name, None)
        if original is None:
            continue
        wrappers[name] = _ToolWrapper(name, original)
    return wrappers


_WRAPPERS: dict[str, _ToolWrapper] = _build_wrappers()


@pytest.fixture(autouse=True)
def _patch_tool_objects(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """Replace each ``@mcp.tool``-decorated name with a 2.x-shaped wrapper.

    Patches both ``mailgun_mcp.main`` and any already-loaded test module so
    that test-side imports (``from mailgun_mcp.main import send_message``)
    see the wrapper, not the raw function.

    Skipped for tests marked ``@pytest.mark.no_tool_wrapper`` (or in modules
    under ``tests/unit/`` that opt-out via the ``profile_test`` marker) — the
    W2b.1 tool-profile wiring tests need access to the raw functions so that
    ``Tool.from_function(fn=...)`` can introspect their signatures without
    hitting the wrapper's ``*args, **kwargs`` rejection.
    """
    marker = request.node.get_closest_marker("no_tool_wrapper")
    if marker is not None:
        return
    for name, wrapper in _WRAPPERS.items():
        monkeypatch.setattr(_main, name, wrapper, raising=False)

        # The test files did ``from mailgun_mcp.main import send_message``
        # at module load, which bound the raw function into their namespace.
        # Patch the local binding on each test module too.
        for module_name, module in list(sys.modules.items()):
            if not module_name.startswith("tests."):
                continue
            if module is None or not hasattr(module, name):
                continue
            current = getattr(module, name, None)
            if current is wrapper or current is None:
                continue
            monkeypatch.setattr(module, name, wrapper, raising=False)
