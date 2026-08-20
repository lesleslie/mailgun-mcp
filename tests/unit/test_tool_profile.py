"""mailgun-mcp tool profile wiring tests.

Verifies the W2b.1 adoption of ``mcp_common.tools.dispatch._apply_tool_profile``
replaces the inline ``@mcp.tool(...)`` decorator mode with a 3-tier
callable-mode architecture (MINIMAL / STANDARD / FULL) gated by the
``MAILGUN_TOOL_PROFILE`` environment variable.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path("/Users/les/Projects/mailgun-mcp")


def test_profiles_py_exists() -> None:
    """profiles.py must exist under mailgun_mcp/tools/."""
    profiles = REPO_ROOT / "mailgun_mcp" / "tools" / "profiles.py"
    assert profiles.exists(), f"{profiles} missing"


def test_profiles_py_defines_profile_registrations() -> None:
    """profiles.py must export a PROFILE_REGISTRATIONS dict."""
    profiles = REPO_ROOT / "mailgun_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    found = False
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "PROFILE_REGISTRATIONS"
                for t in node.targets
            )
        ) or (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "PROFILE_REGISTRATIONS"
        ):
            found = True
            break
    assert found, "PROFILE_REGISTRATIONS not defined in profiles.py"


def test_profiles_py_defines_build_registration_map() -> None:
    """profiles.py must export ``_build_registration_map`` (consumed by main.apply_mailgun_tool_profile)."""
    profiles = REPO_ROOT / "mailgun_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    found = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "_build_registration_map"
        for node in ast.walk(tree)
    )
    assert found, "_build_registration_map not defined in profiles.py"


def test_profiles_py_defines_register_all_tool_groups() -> None:
    """profiles.py must export ``register_all_tool_groups`` (used as register_all_fn at FULL profile)."""
    profiles = REPO_ROOT / "mailgun_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    found = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "register_all_tool_groups"
        for node in ast.walk(tree)
    )
    assert found, "register_all_tool_groups not defined in profiles.py"


def test_main_py_uses_mailgun_tool_profile_env_var() -> None:
    """main.py must reference MAILGUN_TOOL_PROFILE env var (passed to the W0 helper)."""
    server = REPO_ROOT / "mailgun_mcp" / "main.py"
    tree = ast.parse(server.read_text())
    found = any(
        isinstance(node, ast.Constant) and node.value == "MAILGUN_TOOL_PROFILE"
        for node in ast.walk(tree)
    )
    assert found, "MAILGUN_TOOL_PROFILE not referenced in main.py"


def test_main_py_defines_all_eight_register_groups() -> None:
    """main.py must define the eight register_<group>_tools() functions."""
    server = REPO_ROOT / "mailgun_mcp" / "main.py"
    tree = ast.parse(server.read_text())
    expected = {
        "register_send_tools",
        "register_stats_tools",
        "register_events_tools",
        "register_domain_tools",
        "register_routes_tools",
        "register_templates_tools",
        "register_suppression_tools",
        "register_webhook_tools",
    }
    found = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    missing = expected - found
    assert not missing, f"Missing register_<group> functions: {sorted(missing)}"


def test_main_py_has_no_remaining_decorator_mode() -> None:
    """The 31 @mcp.tool(...) decorators must all be replaced by register_* calls."""
    server = REPO_ROOT / "mailgun_mcp" / "main.py"
    tree = ast.parse(server.read_text())
    decorator_count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        for dec in node.decorator_list:
            if (
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Attribute)
                and dec.func.attr == "tool"
                and isinstance(dec.func.value, ast.Name)
                and dec.func.value.id == "mcp"
            ):
                decorator_count += 1
    assert decorator_count == 0, (
        f"Expected 0 @mcp.tool decorators (all refactored); found {decorator_count}"
    )


def test_main_py_wires_apply_tool_profile() -> None:
    """main.py must define ``apply_mailgun_tool_profile`` calling ``_apply_tool_profile``."""
    server = REPO_ROOT / "mailgun_mcp" / "main.py"
    tree = ast.parse(server.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        if node.name != "apply_mailgun_tool_profile":
            continue
        for sub in ast.walk(node):
            if (
                isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Name)
                and sub.func.id == "_apply_tool_profile"
            ):
                found = True
    assert found, "apply_mailgun_tool_profile must await _apply_tool_profile"


def test_main_py_wires_tool_profile_env_var() -> None:
    """The _apply_tool_profile call must pass ``profile_env_var="MAILGUN_TOOL_PROFILE"``."""
    server = REPO_ROOT / "mailgun_mcp" / "main.py"
    tree = ast.parse(server.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Name) and node.func.id == "_apply_tool_profile"):
            continue
        for kw in node.keywords:
            if (
                kw.arg == "profile_env_var"
                and isinstance(kw.value, ast.Constant)
                and kw.value.value == "MAILGUN_TOOL_PROFILE"
            ):
                found = True
    assert found, "_apply_tool_profile call must pass profile_env_var='MAILGUN_TOOL_PROFILE'"


def test_main_py_uses_async_helper_not_sync_wrapper() -> None:
    """Per W1.4 lesson: use ``_apply_tool_profile`` (async helper), NOT ``apply_tool_profile`` (sync wrapper raises in loop)."""
    server = REPO_ROOT / "mailgun_mcp" / "main.py"
    tree = ast.parse(server.read_text())
    sync_call = False
    async_call = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            if node.func.id == "apply_tool_profile":
                sync_call = True
            elif node.func.id == "_apply_tool_profile":
                async_call = True
    assert async_call, "Expected _apply_tool_profile (async helper) call in main.py"
    assert not sync_call, (
        "Found bare apply_tool_profile() call — sync wrapper raises in event loop; "
        "use await _apply_tool_profile() instead"
    )


def test_pyproject_bumps_mcp_common_to_0_18() -> None:
    """mcp-common pin must be >=0.18.0 (the W0 helper version)."""
    pyproject = REPO_ROOT / "pyproject.toml"
    text = pyproject.read_text()
    assert "mcp-common>=0.18.0" in text or 'mcp-common = { version = ">=0.18.0"' in text, (
        "mcp-common pin must be >=0.18.0 in pyproject.toml"
    )


def test_decision_doc_exists_at_tracked_path() -> None:
    """Rationale doc must live at docs/architecture/tool-profile-rationale.md (.claude/ is gitignored)."""
    path = REPO_ROOT / "docs" / "architecture" / "tool-profile-rationale.md"
    assert path.exists(), f"{path} missing"


@pytest.mark.no_tool_wrapper
@pytest.mark.asyncio
async def test_full_registers_all_31_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """FULL profile must register all 31 mailgun tools + discover_tools = 32 total.

    Behavioral parity: original decorator-mode registered 31 tools at import.
    The W0 helper additionally registers ``discover_tools`` (the meta-tool
    the W2b.1 spec requires).
    """
    monkeypatch.setenv("MAILGUN_TOOL_PROFILE", "full")
    from fastmcp import FastMCP

    from mailgun_mcp.main import apply_mailgun_tool_profile

    server = FastMCP(name="Test", instructions="test")
    await apply_mailgun_tool_profile(server)
    names = {t.name for t in await server.list_tools()}

    # All 31 mailgun tools + discover_tools
    expected_mailgun = {
        "send_message",
        "get_domains", "get_domain", "create_domain", "delete_domain", "verify_domain",
        "get_events", "get_stats",
        "get_bounces", "add_bounce", "delete_bounce",
        "get_complaints", "add_complaint", "delete_complaint",
        "get_unsubscribes", "add_unsubscribe", "delete_unsubscribe",
        "get_routes", "get_route", "create_route", "update_route", "delete_route",
        "get_templates", "get_template", "create_template", "update_template", "delete_template",
        "get_webhooks", "get_webhook", "create_webhook", "delete_webhook",
    }
    assert expected_mailgun.issubset(names), (
        f"FULL profile missing tools: {sorted(expected_mailgun - names)}"
    )
    assert "discover_tools" in names, "W0 helper must register discover_tools meta-tool"
    assert len(names) == 32, f"Expected 32 (31 + discover_tools); got {len(names)}: {sorted(names)}"


@pytest.mark.no_tool_wrapper
@pytest.mark.asyncio
async def test_standard_has_18_daily_driver_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """STANDARD profile must register 18 daily-driver tools (no suppression/webhook)."""
    monkeypatch.setenv("MAILGUN_TOOL_PROFILE", "standard")
    from fastmcp import FastMCP

    from mailgun_mcp.main import apply_mailgun_tool_profile

    server = FastMCP(name="Test", instructions="test")
    await apply_mailgun_tool_profile(server)
    names = {t.name for t in await server.list_tools()}

    # 18 daily-driver tools present
    daily_driver = {
        "send_message",
        "get_stats", "get_events",
        "get_domains", "get_domain", "create_domain", "delete_domain", "verify_domain",
        "get_routes", "get_route", "create_route", "update_route", "delete_route",
        "get_templates", "get_template", "create_template", "update_template", "delete_template",
    }
    assert daily_driver.issubset(names), (
        f"STANDARD missing daily-driver: {sorted(daily_driver - names)}"
    )
    # FULL-only groups absent
    suppression_or_webhook = {
        "get_bounces", "add_bounce", "delete_bounce",
        "get_complaints", "add_complaint", "delete_complaint",
        "get_unsubscribes", "add_unsubscribe", "delete_unsubscribe",
        "get_webhooks", "get_webhook", "create_webhook", "delete_webhook",
    }
    assert not (suppression_or_webhook & names), (
        f"STANDARD leaked FULL-only tools: {sorted(suppression_or_webhook & names)}"
    )
    assert "discover_tools" in names


@pytest.mark.no_tool_wrapper
@pytest.mark.asyncio
async def test_minimal_has_only_discover_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """MINIMAL profile registers only ``discover_tools`` (no mailgun domain tools)."""
    monkeypatch.setenv("MAILGUN_TOOL_PROFILE", "minimal")
    from fastmcp import FastMCP

    from mailgun_mcp.main import apply_mailgun_tool_profile

    server = FastMCP(name="Test", instructions="test")
    await apply_mailgun_tool_profile(server)
    names = {t.name for t in await server.list_tools()}

    assert names == {"discover_tools"}, (
        f"MINIMAL must only register discover_tools; got: {sorted(names)}"
    )


def test_profile_registrations_subset_of_map() -> None:
    """Every key referenced in PROFILE_REGISTRATIONS must exist in REGISTRATION_MAP."""
    from mcp_common.tools import ToolProfile

    from mailgun_mcp.tools.profiles import _build_registration_map

    mapping = _build_registration_map()
    for profile, regs in {
        ToolProfile.STANDARD: [
            "send_tools", "stats_tools", "events_tools", "domain_tools",
            "routes_tools", "templates_tools",
        ],
        ToolProfile.FULL: [
            "send_tools", "stats_tools", "events_tools", "domain_tools",
            "routes_tools", "templates_tools", "suppression_tools", "webhook_tools",
        ],
    }.items():
        for group in regs:
            assert group in mapping, (
                f"{profile.value} references group {group!r} but REGISTRATION_MAP "
                f"is missing it; keys={sorted(mapping)}"
            )
