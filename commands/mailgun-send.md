---
description: Send an email message via the Mailgun API with optional cc/bcc/html/attachments/tags/scheduled delivery.
argument-hint: <from> <to> <subject> <text> [--cc ...] [--bcc ...] [--html ...] [--attachment PATH] [--tag TAG] [--schedule-at RFC2822]
allowed-tools: mcp__mailgun__send_message
---

# /mailgun-send

Send an email message via the Mailgun API using the `mailgun` MCP server.

## Usage

`/mailgun-send <from> <to> <subject> <text> [--cc ...] [--bcc ...] [--html ...] [--attachment PATH] [--tag TAG] [--schedule-at RFC2822]`

Arguments:

- `<from>`: sender address (e.g. `"Acme <[email protected]>"`).
- `<to>`: comma-separated recipient list.
- `<subject>`: email subject line.
- `<text>`: plain-text body. Required even when an HTML body is supplied.
- `--cc`: optional comma-separated CC list.
- `--bcc`: optional comma-separated BCC list.
- `--html`: optional HTML body. When provided, both `<text>` and `--html` are sent as alternative bodies.
- `--attachment`: optional absolute path to a file to attach. Max 25 MB; optional ClamAV scan is run if `clamd` is available.
- `--tag`: optional Mailgun tag (`o:tag`) for analytics routing.
- `--schedule-at`: optional RFC 2822 delivery time (`o:schedule`).

## Prerequisites

- `MAILGUN_API_KEY` and `MAILGUN_DOMAIN` must be set in the server's environment. The MCP server exits on startup if either is missing.
- The server binds HTTP transport to `http://localhost:3039/mcp` by default.

## Workflow

1. Confirm the `mailgun` MCP server is reachable (`curl http://localhost:3039/healthz`).
2. Call `mcp__mailgun__send_message` with `from_email`, `to`, `subject`, `text`, and any optional flags.
3. Return the Mailgun message ID and storage URL from the response payload.

## Example

```
/mailgun-send "[email protected]" "[email protected]" "Hello from Mailgun MCP" "Plain text body" --html "<p>HTML body</p>" --tag welcome
```
