---
schema: agent
table: agent_memory_registry
id: 020887b1-5d3d-46ee-81f4-a248a744f7dc
agent: Captain Mod
memory_type: constraint
key: prevent-agent-1c497f1c
created: 2026-06-11T16:06:49.612866+00:00
updated: 2026-06-11T16:06:49.612866+00:00
quality_score: 51.0
quality_grade: F
---

# 🤖 Captain Mod — prevent-agent-1c497f1c

## Metadata

| Field | Value |
|---|---|
| ID | `020887b1-5d3d-46ee-81f4-a248a744f7dc` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-agent-1c497f1c` |
| Confidence | 1.00 |
| Source | enrichment-engine-agent |
| Created | 2026-06-11T16:06:49.612866+00:00 |
| Updated | 2026-06-11T16:06:49.612866+00:00 |

## Value

{
  "source_id": "1c497f1c-5938-40c9-83fc-c51efc84ddb9",
  "source_schema": "agent",
  "preventive_rule": "{'text': 'Telegram bot tokens can only be consumed by one Hermes instance. Before deploying, always verify token uniqueness across all environments.'}"
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **51.0** / 100 (F) |
| Evidence | 7.0 / 20 |
| Impact | 16 / 20 |
| Reuse | 6.0 / 20 |
| Confidence | 16.0 / 20 |
| Actionability | 6.0 / 20 |
| Updated | 2026-06-11T16:12:06.412028+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `020887b1-5d3d-46ee-81f4-a248a744f7dc`
