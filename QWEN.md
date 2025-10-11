# Mailgun MCP Server - Qwen Code Context

## Project Overview

This is a Mailgun MCP (Model Context Protocol) server built with FastMCP and FastAPI. It provides a comprehensive HTTP interface to the full Mailgun API, acting as a proxy service that handles authentication and request forwarding. The application is a lightweight FastAPI proxy that forwards email sending requests and other Mailgun API operations to the Mailgun API.

### Key Technologies

- Python 3.13+
- FastMCP (Model Context Protocol framework)
- FastAPI
- httpx (for async HTTP requests)
- uv (dependency management)
- uvicorn (ASGI server)

### Project Structure

```
mailgun-mcp/
├── pyproject.toml      # Dependency management with uv
├── uv.lock            # Lock file for dependencies
├── .envrc             # direnv configuration (uses layout uv)
├── README.md          # Basic usage instructions
├── AGENTS.md          # Development guidelines for AI agents
├── CLAUDE.md          # Claude-specific development context
├── GEMINI.md          # Gemini-specific development context (if exists)
├── QWEN.md            # This file - Qwen-specific development context
├── mailgun_mcp/       # Main application package
│   ├── __init__.py
│   └── main.py        # Main FastAPI application with comprehensive Mailgun API
├── tests/             # Test suite
│   ├── __init__.py
│   └── test_main.py   # Tests for main application
```

## Core Components

### `mailgun_mcp/main.py`

The main FastMCP application with multiple tools for interacting with the Mailgun API:

- **Email Management**:

  - `send_message` - Send emails via Mailgun API with support for attachments, tags, and scheduled delivery

- **Domain Management**:

  - `get_domains` - Get a list of domains
  - `get_domain` - Get information about a specific domain
  - `create_domain` - Create a new domain
  - `delete_domain` - Delete a domain
  - `verify_domain` - Verify a domain

- **Email Events & Logs**:

  - `get_events` - Get email events (opens, clicks, deliveries, etc.)

- **Statistics & Metrics**:

  - `get_stats` - Get email statistics

- **Suppression Management**:

  - `get_bounces`, `add_bounce`, `delete_bounce` - Bounce list management
  - `get_complaints`, `add_complaint`, `delete_complaint` - Complaints management
  - `get_unsubscribes`, `add_unsubscribe`, `delete_unsubscribe` - Unsubscribe management

- **Routes Management**:

  - `get_routes`, `get_route` - List and get specific routes
  - `create_route`, `update_route`, `delete_route` - Route management

- **Template Management**:

  - `get_templates`, `get_template` - List and get specific templates
  - `create_template`, `update_template`, `delete_template` - Template management

- **Webhook Management**:

  - `get_webhooks`, `get_webhook` - List and get specific webhooks
  - `create_webhook`, `delete_webhook` - Webhook management

### Key Environment Variables

- `MAILGUN_API_KEY` - Your Mailgun API key
- `MAILGUN_DOMAIN` - Your Mailgun domain name

## Development Workflow

### Setup & Dependencies

```bash
# Install dependencies using uv
uv sync

# Install dev dependencies too
uv sync --dev
```

### Running the Application

```bash
# Set required environment variables
export MAILGUN_API_KEY="your-api-key"
export MAILGUN_DOMAIN="your-domain"

# Run development server with auto-reload
uvicorn mailgun_mcp.main:app --reload

# Alternative: Run with inline credentials
MAILGUN_API_KEY=... MAILGUN_DOMAIN=... uvicorn mailgun_mcp.main:app --reload
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_main.py::test_send_message_requires_credentials

# Run tests with verbose output
uv run pytest -v

# Stop after first failure
uv run pytest --maxfail=1
```

## Development Conventions

### Code Style

- Follow PEP 8: 4-space indentation, snake_case for modules/functions
- Keep endpoints async and properly typed
- Use descriptive constant names for environment keys
- Prefer small, composable helpers over long route handlers
- Document non-obvious logic with concise docstrings

### Testing Strategy

- Use pytest with filenames prefixed by `test_`
- Structure async tests with `pytest.mark.asyncio`
- Leverage `httpx.AsyncClient` mocks to avoid outbound calls during testing
- Add regression tests for Mailgun request formatting or response handling changes
- Target meaningful coverage of validation and error paths

### Commit & PR Guidelines

- Use Conventional Commit subjects (e.g., `feat: add mail sending route`)
- Reference issues in the body (`Fixes #12`) and mention environment changes
- Include test coverage information in PRs
- Ensure test suite stays green before pushing

### Security & Configuration

- Store `MAILGUN_API_KEY` and `MAILGUN_DOMAIN` in shell profile or secrets manager
- Never commit plaintext credentials
- Rotate API keys after testing
- Redact sensitive data from logs when sharing

## Architecture Details

The application is a comprehensive FastMCP proxy that:

1. **Authentication**: Uses environment variables `MAILGUN_API_KEY` and `MAILGUN_DOMAIN` for Mailgun API access
1. **Request Handling**: Accepts tool calls and forwards to appropriate Mailgun API endpoints
1. **Error Handling**: Returns clear error messages when credentials are missing
1. **HTTP Client**: Uses httpx AsyncClient for external API calls to Mailgun
1. **Configuration**: All configuration is loaded from environment variables

## Testing Approach

Tests use monkeypatch to mock:

- Environment variables for credential testing
- httpx.AsyncClient for API call testing without external dependencies

The test suite covers both error conditions (missing credentials) and successful message forwarding scenarios for all implemented API endpoints.
