---
schema: agent
table: agent_memory_registry
id: 6eebf5a3-00d3-4745-a5c8-e52c0045208b
agent: Captain Mod
memory_type: constraint
key: prevent-failure-b0d58855
created: 2026-06-11T16:06:49.533183+00:00
updated: 2026-06-11T16:06:49.533183+00:00
quality_score: 50.4
quality_grade: F
---

# 🤖 Captain Mod — prevent-failure-b0d58855

## Metadata

| Field | Value |
|---|---|
| ID | `6eebf5a3-00d3-4745-a5c8-e52c0045208b` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-failure-b0d58855` |
| Confidence | 0.95 |
| Source | enrichment-engine-failure |
| Created | 2026-06-11T16:06:49.533183+00:00 |
| Updated | 2026-06-11T16:06:49.533183+00:00 |

## Value

{
  "source_id": "b0d58855-d455-4155-9436-7c2099a3f5d4",
  "source_schema": "failure",
  "preventive_rule": "Prevention for telegram-bot: Never configure two Hermes instances with the same Telegram bot token. One bot [REDACTED] active consumer."
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
| Updated | 2026-06-11T16:12:06.405613+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `6eebf5a3-00d3-4745-a5c8-e52c0045208b`
