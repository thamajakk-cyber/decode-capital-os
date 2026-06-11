---
schema: failure
table: failure_registry
id: b0d58855-d455-4155-9436-7c2099a3f5d4
system: telegram-bot
failure_type: integration
severity: high
status: resolved
created: 2026-06-11T15:39:32.072640+00:00
---

# ❌ telegram-bot — integration

## Metadata

| Field | Value |
|---|---|
| ID | `b0d58855-d455-4155-9436-7c2099a3f5d4` |
| System | telegram-bot |
| Type | integration |
| Severity | high |
| Date | 2026-06-11T15:39:32.072640+00:00 |
| Status | resolved |
| Created | 2026-06-11T15:39:32.072640+00:00 |

## Symptom

Two Hermes instances polling same Telegram bot token simultaneously

## Root Cause

{"text": "Both host Hermes and Docker Hermes agent were configured with the same TELEGRAM_BOT_TOKEN. Telegram only allows one consumer per bot token. Both instances competed for updates, causing mutual polling conflicts and message delivery failures."}

## Evidence

```json
{}
```

## Fix Applied

Commented TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS, TELEGRAM_HOME_CHANNEL in Docker agent .env file. Host Hermes remains sole Telegram consumer.

## Verification

Verified: Docker agent no longer polls Telegram. Host Hermes sole consumer confirmed via gateway logs.

## Preventive Rule

Never configure two Hermes instances with the same Telegram bot token. One bot [REDACTED] active consumer.

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `b0d58855-d455-4155-9436-7c2099a3f5d4`
