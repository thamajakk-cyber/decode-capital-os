---
schema: agent
table: agent_memory_registry
id: 54620bdb-33c7-4ce4-9a40-eece36648c23
agent: Captain Mod
memory_type: constraint
key: prevent-telegram-dual-polling
created: 2026-06-11T15:45:33.887357+00:00
updated: 2026-06-11T15:45:33.887357+00:00
quality_score: 47.0
quality_grade: F
---

# 🤖 Captain Mod — prevent-telegram-dual-polling

## Metadata

| Field | Value |
|---|---|
| ID | `54620bdb-33c7-4ce4-9a40-eece36648c23` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-telegram-dual-polling` |
| Confidence | 1.00 |
| Source | rcaf-engine |
| Created | 2026-06-11T15:45:33.887357+00:00 |
| Updated | 2026-06-11T15:45:33.887357+00:00 |

## Value

{
  "fix_summary": "Commented TELEGRAM_BOT_TOKEN in Docker agent .env file",
  "preventive_rule": "One Telegram bot [REDACTED] active consumer. Verify token uniqueness before deploying.",
  "root_cause_summary": "Host Hermes and Docker Hermes both configured with same TELEGRAM_BOT_TOKEN"
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **47.0** / 100 (F) |
| Evidence | 5.0 / 20 |
| Impact | 16 / 20 |
| Reuse | 6.0 / 20 |
| Confidence | 14.0 / 20 |
| Actionability | 6.0 / 20 |
| Updated | 2026-06-11T15:52:45.583513+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `54620bdb-33c7-4ce4-9a40-eece36648c23`
