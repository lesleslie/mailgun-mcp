# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-08-20

### Added

- mailgun-mcp: Adopt apply_tool_profile with MAILGUN_TOOL_PROFILE
- mailgun: Bodai plugin conversion (manifest, mcp.json, slash commands)

### Fixed

- mailgun-mcp: Reviewer fixes round 1 — banner gating, fixture deletion
- mailgun-mcp: Ruff cleanup + disable destructive fix mode
- mailgun-mcp: Untrack .pyscn/reports/ artifacts

### Documentation

- mailgun-mcp: Update CLAUDE.md + rationale for round 1 fixture deletion

### Internal

- Gitignore runtime artifacts + untrack previously-tracked cache files (bodai cleanup 2026-08-17)
- gitignore: Untrack .pyscn/ (bodai 2026-08-20)
- mailgun-mcp: Bootstrap [tool.crackerjack] section + uv sync upgrade
- mailgun-mcp: Gitignore .lycheecache (file, not just dir)
- mailgun-mcp: Gitignore .lycheecache + .hypothesis
- mailgun-mcp: Refresh oneiric + mcp-common deps
- mailgun-mcp: Untrack .lycheecache + .hypothesis runtime artifacts
- Untrack previously-tracked runtime artifacts (bodai cleanup 2026-08-17)

## [0.3.1] - 2026-08-16

### Documentation

- Fix quickstart commands, tool counts, port/env vars, badge

### Internal

- Untrack backup files (.backup, .backup.json, .bak)

## [0.3.0] - 2026-08-12

### Changed

- Mailgun-mcp (quality: 56/100) - 2026-06-19 08:10:00

### Fixed

- Add ty: ignore for BasicAuth arg type (or "" doesn't narrow to str)
- Address test failure and C901 complexity
- Drop unused # type: ignore directives

### Internal

- Adopt register_http_health_route from mcp-common
- Bump oneiric dep to >=0.16.0
- Fix pre-existing test failures surfaced by FastMCP 3.x bump
- mailgun-mcp: Migrate # type: ignore stragglers to ty syntax or fix
- Use __version__ instead of hardcoded version literal

## [0.2.8] - 2026-06-19

### Internal

- Add .cache dir for gitleaks quality tooling
- gitignore: Add backup file patterns to silence checkpoint tool artifacts
- Untrack and delete 2 historical *.backup/*.bak files

## [0.2.7] - 2026-05-10

### Changed

- Mailgun-mcp (quality: 62/100) - 2025-10-11 05:13:06
- Mailgun-mcp (quality: 70/100) - 2026-01-05 11:49:11
- Mailgun-mcp (quality: 70/100) - 2026-01-22 11:45:22
- Migrate mailgun-mcp to mcp-common v0.4.4
- Update config, core
- Update config, core
- Update config, core, deps
- Update config, core, deps
- Update config, core, deps, docs
- Update config, core, deps, tests
- Update config, core, deps, tests
- Update config, deps
- Update core functionality

### Testing

- test: Update 23 files

### Internal

- Bump version to 0.1.2
- Bump version to 0.1.3
- Bump version to 0.2.0
- Bump version to 0.2.1
- Bump version to 0.2.2
- Bump version to 0.2.3
- Bump version to 0.2.4
- Bump version to 0.2.5
- Update LICENSE copyright to 2026

## [0.2.6] - 2026-05-10

### Internal

- Update LICENSE copyright to 2026

## [0.2.5] - 2026-01-24

### Changed

- Update config, core, deps

## [0.2.4] - 2026-01-22

### Changed

- Mailgun-mcp (quality: 70/100) - 2026-01-22 11:45:22
- Update config, core

## [0.2.3] - 2026-01-05

### Changed

- Mailgun-mcp (quality: 70/100) - 2026-01-05 11:49:11
- Update config, core

## [0.2.2] - 2026-01-05

### Changed

- Update config, core, deps

## [0.2.1] - 2026-01-04

### Changed

- Update config, core, deps, tests

## [0.2.0] - 2026-01-03

### Changed

- Migrate mailgun-mcp to mcp-common v0.4.4
- Update config, core, deps, tests

## [0.1.3] - 2025-12-20

### Changed

- Update config, core, deps, docs
- Update config, deps
- Update core functionality

### Internal

- Bump version to 0.1.2
