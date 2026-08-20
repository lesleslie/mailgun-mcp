---
description: List, inspect, create, verify, or delete Mailgun domains for the configured account.
argument-hint: list | get <domain> | create <name> <smtp-password> [--spam-action disabled|tag|block] [--wildcard] | verify <domain> | delete <domain>
allowed-tools: mcp__mailgun__get_domains, mcp__mailgun__get_domain, mcp__mailgun__create_domain, mcp__mailgun__verify_domain, mcp__mailgun__delete_domain
---

# /mailgun-domains

Inspect and manage Mailgun sending domains.

## Usage

`/mailgun-domains <action> [args...]`

Actions:

- `list`: paginate all domains via `mcp__mailgun__get_domains`. Optional flags `--limit N` and `--skip N`.
- `get <domain>`: fetch a single domain record via `mcp__mailgun__get_domain`.
- `create <name> <smtp-password>`: register a new domain via `mcp__mailgun__create_domain`. Optional flags `--spam-action disabled|tag|block` and `--wildcard` to enable catch-all routing.
- `verify <domain>`: trigger DNS verification via `mcp__mailgun__verify_domain`. Mailgun will re-check the required MX/TXT records.
- `delete <domain>`: remove a domain via `mcp__mailgun__delete_domain`. Irreversible.

## Workflow

1. For `list`, call `mcp__mailgun__get_domains` with the requested `limit`/`skip` and present the `items` array.
2. For `get`, call `mcp__mailgun__get_domain` with `domain_name`.
3. For `create`, call `mcp__mailgun__create_domain` with the new domain name, SMTP password, and any optional flags. Surface the `domain` payload (especially `smtp_login`, `wildcard`, `spam_action`).
4. For `verify`, call `mcp__mailgun__verify_domain` and report the `status` field from the response.
5. For `delete`, call `mcp__mailgun__delete_domain` and confirm `"message": "domain deleted"` in the response.

## Prerequisites

- `MAILGUN_API_KEY` must be set. `MAILGUN_DOMAIN` is not required for the listing/inspection actions but must match a domain you own before sending mail through it.

## Example

```
/mailgun-domains list --limit 25
/mailgun-domains get mg.example.com
/mailgun-domains verify mg.example.com
```
