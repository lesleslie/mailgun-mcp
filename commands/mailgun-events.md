---
description: Fetch Mailgun delivery events (accepts/delivered/opened/clicked/bounced/etc.) and aggregate statistics for a domain.
argument-hint: events <domain> [--event ...] [--begin RFC2822] [--end RFC2822] [--limit N] | stats <domain> --event <event[,event...]> --start RFC2822 [--end RFC2822] [--resolution hour|day|month] [--duration 30d|7d|...].
allowed-tools: mcp__mailgun__get_events, mcp__mailgun__get_stats
---

# /mailgun-events

Query Mailgun event logs (`get_events`) and aggregate statistics (`get_stats`) for a single domain.

## Usage

`/mailgun-events <mode> <domain> [flags...]`

Two modes:

- `events`: fetch raw event log entries.
- `stats`: fetch aggregate counters grouped by resolution bucket.

### Events mode

`/mailgun-events events <domain> [--event <type>] [--begin RFC2822] [--end RFC2822] [--limit N] [--ascending yes|no]`

- `--event`: filter by event type. Repeat to OR multiple types (e.g. `--event opened --event clicked`). Supported types include `accepted`, `delivered`, `opened`, `clicked`, `bounced`, `complained`, `unsubscribed`, `failed`.
- `--begin` / `--end`: RFC 2822 timestamps bounding the window (default last 30 days if omitted).
- `--limit`: max records to return (server default 100).
- `--ascending`: `yes` returns oldest-first; default is newest-first.

### Stats mode

`/mailgun-events stats <domain> --event <event[,event...]> --start RFC2822 [--end RFC2822] [--resolution hour|day|month] [--duration 30d|7d|...]`

- `--event`: required, comma-separated list of event types to aggregate (same vocabulary as `events` mode).
- `--start`: required, RFC 2822 timestamp.
- `--end`: optional, RFC 2822 timestamp (defaults to "now").
- `--resolution`: bucket size (`hour`, `day`, `month`).
- `--duration`: shortcut window like `30d`, `7d`, `1h`. When supplied, the server computes `--start` for you.

## Workflow

1. Confirm `<domain>` is a verified sending domain (use `/mailgun-domains get <domain>` if unsure).
2. For `events`, call `mcp__mailgun__get_events` with `domain_name` and the supplied filters. Surface the `items` array and total count.
3. For `stats`, call `mcp__mailgun__get_stats` with `domain_name`, `event`, and `start`. Surface the time-bucketed counters in the response.

## Prerequisites

- `MAILGUN_API_KEY` must be set. The `domain_name` argument is the sending domain (e.g. `mg.example.com`), not the API root domain.

## Example

```
/mailgun-events events mg.example.com --event opened --event clicked --limit 50
/mailgun-events stats mg.example.com --event delivered,opened --start "Thu, 01 Jan 2026 00:00:00 -0000" --resolution day
```
