# Repository Guidelines

## Project Structure & Module Organization

Keep FastAPI entrypoints inside `mailgun_mcp/main.py`, with lightweight route handlers that delegate to helpers in sibling modules (e.g., `mailgun_mcp/email.py` for Mailgun payload assembly). Shared utilities belong under `mailgun_mcp/` so the API layer stays thin and testable. Tests live in `tests/` and should mirror the package layout (`tests/test_main.py` for the main app). Project metadata stays in the repository root (`pyproject.toml`, `uv.lock`), and no secrets should be committed.

## Build, Test, and Development Commands

Run `uv sync` after changing dependencies to install Python 3.13 packages. Start the local server with `uv run uvicorn mailgun_mcp.main:app --reload` for hot reloading. Execute the suite via `uv run pytest` (add `-k keyword` to focus specific cases). When smoke-testing Mailgun calls, supply credentials inline: `MAILGUN_API_KEY=... MAILGUN_DOMAIN=... uv run uvicorn mailgun_mcp.main:app --reload`.

## Coding Style & Naming Conventions

Follow PEP 8 with 4-space indentation, snake_case for functions and modules, and CapWords for classes. Keep endpoints async, annotate request/response models, and favor dependency-injected helpers to avoid long handler bodies. Add concise docstrings for logic that is not obvious, and keep environment variable names descriptive (`MAILGUN_API_KEY`, `MAILGUN_DOMAIN`).

## Testing Guidelines

Use `pytest` with filenames prefixed by `test_`. Mark async cases with `@pytest.mark.asyncio` and patch HTTP calls using `httpx.AsyncClient` fixtures or mocks. Add regression coverage whenever modifying Mailgun request formatting or error handling, and run `uv run pytest --maxfail=1` before pushing to ensure a clean run.

## Commit & Pull Request Guidelines

Adopt Conventional Commit subjects (`feat: add mail sending route`, `fix: handle missing domain`). Reference related issues in the body (`Fixes #12`), call out environment changes, and document testing performed. Pull requests should summarize behavioral impact, include relevant logs or Mailgun samples when available, and confirm that CI (when enabled) passes.

## Security & Configuration Tips

Store credentials outside the repo (shell profile, secrets manager) and keep `.env` files untracked. Rotate Mailgun keys after live testing, avoid pasting message payloads into shared logs, and scrub recipient data before sharing troubleshooting artifacts.
