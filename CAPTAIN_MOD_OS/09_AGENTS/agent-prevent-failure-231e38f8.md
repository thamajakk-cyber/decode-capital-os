---
schema: agent
table: agent_memory_registry
id: 4a68d8a3-ac88-459d-af62-c4ae834b2a47
agent: Captain Mod
memory_type: constraint
key: prevent-failure-231e38f8
created: 2026-06-11T16:06:49.535836+00:00
updated: 2026-06-11T16:06:49.535836+00:00
quality_score: 50.4
quality_grade: F
---

# 🤖 Captain Mod — prevent-failure-231e38f8

## Metadata

| Field | Value |
|---|---|
| ID | `4a68d8a3-ac88-459d-af62-c4ae834b2a47` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-failure-231e38f8` |
| Confidence | 0.95 |
| Source | enrichment-engine-failure |
| Created | 2026-06-11T16:06:49.535836+00:00 |
| Updated | 2026-06-11T16:06:49.535836+00:00 |

## Value

{
  "source_id": "231e38f8-94dd-4422-8fd2-b33f3b657650",
  "source_schema": "failure",
  "preventive_rule": "Prevention for telegram-bot: One Telegram bot [REDACTED] active consumer. Verify token uniqueness before deploying."
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **50.4** / 100 (F) |
| Evidence | 7.0 / 20 |
| Impact | 16 / 20 |
| Reuse | 6.0 / 20 |
| Confidence | 15.4 / 20 |
| Actionability | 6.0 / 20 |
| Updated | 2026-06-11T16:07:25.738988+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `4a68d8a3-ac88-459d-af62-c4ae834b2a47`
