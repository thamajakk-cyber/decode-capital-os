---
schema: failure
table: failure_registry
id: 231e38f8-94dd-4422-8fd2-b33f3b657650
system: telegram-bot
failure_type: infrastructure
severity: high
status: resolved
created: 2026-06-11T15:45:33.871636+00:00
---

# ❌ telegram-bot — infrastructure

## Metadata

| Field | Value |
|---|---|
| ID | `231e38f8-94dd-4422-8fd2-b33f3b657650` |
| System | telegram-bot |
| Type | infrastructure |
| Severity | high |
| Date | 2026-06-11T15:45:33.871636+00:00 |
| Status | resolved |
| Created | 2026-06-11T15:45:33.871636+00:00 |

## Symptom

Two Hermes instances polling same Telegram bot token simultaneously causing mutual message delivery failures

## Root Cause

{"text": "Host Hermes and Docker Hermes both configured with same TELEGRAM_BOT_TOKEN"}

## Evidence

```json
{}
```

## Fix Applied

Commented TELEGRAM_BOT_TOKEN in Docker agent .env file

## Verification

Verified Docker agent no longer polls Telegram. Host Hermes sole consumer confirmed.

## Preventive Rule

One Telegram bot [REDACTED] active consumer. Verify token uniqueness before deploying.

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `231e38f8-94dd-4422-8fd2-b33f3b657650`
