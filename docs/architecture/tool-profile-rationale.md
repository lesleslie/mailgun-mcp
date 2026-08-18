# Tool profile rationale — mailgun-mcp

**Status:** Adopted 2026-08-18 (W2b.1, task 7)
**Owner:** mailgun-mcp maintainers
**Helper:** `mcp_common.tools.dispatch._apply_tool_profile` (mcp-common 0.18.0+)

## Why

mailgun-mcp previously exposed all **31 tools** to every client via inline
`@mcp.tool(...)` decorators registered at module import. The Bodai
ecosystem has standardized on the W0 helper (`_apply_tool_profile`)
to gate tool visibility per client. This document records the 3-tier
mapping adopted in W2b.1.

## Tier mapping

| Tier | Groups | Tool count | Use case |
|------|--------|------------|----------|
| `MINIMAL` | (none) | 0 mailgun tools | Health-only probes; emergency read-only debugging |
| `STANDARD` | send, stats, events, domain, routes, templates | 18 tools | Daily-driver dev work; mirrors the original "common workflow" subset |
| `FULL` | All STANDARD + suppression, webhook | 31 tools | Advanced ops; CI tooling that needs suppression management or webhook rotation |

The grouping mirrors the Mailgun API surface domain structure:

- **send_tools** (1) — outbound email (the original primary use case)
- **stats_tools** (1) — aggregate reporting
- **events_tools** (1) — event log queries
- **domain_tools** (5) — domain CRUD + verification
- **routes_tools** (5) — route CRUD
- **templates_tools** (5) — template CRUD
- **suppression_tools** (9) — bounce / complaint / unsubscribe management
- **webhook_tools** (4) — webhook CRUD

**Why suppression + webhook are FULL-only:** both are write operations that
mutate Mailgun's delivery configuration. The brief explicitly classifies
them as FULL-only, matching Crackerjack's pattern where advanced
groups stay out of the STANDARD tier.

## Why this matters

- **Context reduction.** STANDARD (19 tools with `discover_tools`) vs FULL
  (32 tools) is a 41 % reduction in tool descriptions sent on every MCP
  initialize handshake. Useful for daily-driver Claude sessions.
- **Behavioral parity.** FULL profile registers exactly the same 31 mailgun
  tool names as the pre-refactor decorator-mode path (verified by the
  `test_full_registers_all_31_tools` assertion in
  `tests/unit/test_tool_profile.py`, which pins the full tool-name set
  inline). No regression in capability for operators that opt into FULL.
- **Discoverability.** `discover_tools` meta-tool (auto-registered by the
  W0 helper) returns the live tool list with descriptions, so clients can
  confirm what their tier exposes.

## Configuration precedence

1. **Environment variable** `MAILGUN_TOOL_PROFILE` — `minimal` /
   `standard` / `full`. Default `full` if unset (matches the pre-refactor
   behavior of "register everything").
1. (Future) `settings/local.yaml` `tool_profile:` — supported via
   `yaml_loader=` parameter to the W0 helper, not currently wired in
   mailgun-mcp (matches the ecosystem convention of env-var-first).

## Migration notes

- mailgun-mcp has no MCP-registered health tools (only the `/healthz`
  HTTP route registered via `register_http_health_route` from mcp-common).
  `MAILGUN_MANDATORY_GROUPS` is therefore an empty set, and
  `essential_tool_names=set()` opts out of the subset check.
- The startup banner at module import is now gated behind
  `MAILGUN_TOOL_PROFILE in {"", "full"}` (W2b.1 round 1-fix). Under
  MINIMAL/STANDARD the banner prints
  `profile=<X> — see startup log for actual tool count` instead of the
  misleading hardcoded `31`. The W0 helper's startup log
  (`Applied MAILGUN_TOOL_PROFILE=... → N tools registered`) is the
  source of truth for the actual count.
- The `tests/conftest.py::_patch_tool_objects` autouse fixture wraps
  every `mailgun_mcp.main` tool name in a `_ToolWrapper` for FastMCP 2.x
  test compatibility. The W2b.1 wiring tests opt out via
  `@pytest.mark.no_tool_wrapper` so that `Tool.from_function(fn=...)`
  sees the raw function (the wrapper's `*args, **kwargs` signature
  trips FastMCP's "Functions with \*args are not supported as tools"
  validator).

## References

- Task brief: `.superpowers/sdd/2026-08-18-mcp-tool-profile-adoption/task-7-brief.md`
- W2a template (Crackerjack retrofit): task-6-report.md
- W1.4 reference (Akosha callable-mode retrofit): task-4-report.md
- mcp-common W0 helper: `/Users/les/Projects/mcp-common/mcp_common/tools/dispatch.py`
- Behavioral parity assertion: `tests/unit/test_tool_profile.py::test_full_registers_all_31_tools`
