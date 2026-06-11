---
schema: failure
table: failure_registry
id: b783c5ce-9c36-4a53-b973-18e2ec10b5b9
system: hermes-workspace-telegram
failure_type: integration
severity: high
status: verified
created: 2026-06-11T15:07:49.841401+00:00
---

# ❌ hermes-workspace-telegram — integration

## Metadata

| Field | Value |
|---|---|
| ID | `b783c5ce-9c36-4a53-b973-18e2ec10b5b9` |
| System | hermes-workspace-telegram |
| Type | integration |
| Severity | high |
| Date | 2026-06-11T06:30:00+00:00 |
| Status | verified |
| Created | 2026-06-11T15:07:49.841401+00:00 |

## Symptom

Telegram polling conflict: terminated by other getUpdates request

## Root Cause

Host Hermes and Docker Hermes both used the same Telegram bot token, causing mutual polling conflicts.

## Evidence

```json
{
  "error": "Conflict: terminated by other getUpdates request",
  "token": "shared",
  "instances": 2
}
```

## Fix Applied

Disabled Telegram in Docker agent .env (commented TELEGRAM_BOT_TOKEN). Host Hermes remains sole Telegram consumer.

## Verification

Zero polling conflicts after restart. Agent platforms: api_server only.

## Preventive Rule

One bot [REDACTED] active consumer. If multiple Hermes instances exist, disable Telegram in all but one.

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `b783c5ce-9c36-4a53-b973-18e2ec10b5b9`
