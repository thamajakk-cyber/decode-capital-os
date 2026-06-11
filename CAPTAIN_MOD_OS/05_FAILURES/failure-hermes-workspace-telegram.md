---
schema: failure
table: failure_registry
id: b783c5ce-9c36-4a53-b973-18e2ec10b5b9
system: hermes-workspace-telegram
failure_type: integration
severity: high
status: verified
created: 2026-06-11T15:07:49.841401+00:00
quality_score: 66.0
quality_grade: D
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

## Quality Score

| Metric | Score |
|---|---|
| Total | **66.0** / 100 (D) |
| Evidence | 13.0 / 20 |
| Impact | 15 / 20 |
| Reuse | 15.0 / 20 |
| Confidence | 6.0 / 20 |
| Actionability | 17.0 / 20 |
| Updated | 2026-06-11T15:52:45.573103+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `b783c5ce-9c36-4a53-b973-18e2ec10b5b9`
