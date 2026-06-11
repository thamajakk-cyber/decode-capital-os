---
schema: agent
table: agent_memory_registry
id: 1c497f1c-5938-40c9-83fc-c51efc84ddb9
agent: Captain Mod
memory_type: constraint
key: telegram-single-consumer-rule
created: 2026-06-11T15:39:51.327720+00:00
updated: 2026-06-11T15:39:51.327720+00:00
quality_score: 57.0
quality_grade: F
---

# 🤖 Captain Mod — telegram-single-consumer-rule

## Metadata

| Field | Value |
|---|---|
| ID | `1c497f1c-5938-40c9-83fc-c51efc84ddb9` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `telegram-single-consumer-rule` |
| Confidence | 1.00 |
| Source | founder-example |
| Created | 2026-06-11T15:39:51.327720+00:00 |
| Updated | 2026-06-11T15:39:51.327720+00:00 |

## Value

{
  "text": "Telegram bot tokens can only be consumed by one Hermes instance. Before deploying, always verify token uniqueness across all environments.",
  "enrichment": {
    "rule": "{'text': 'Telegram bot tokens can only be consumed by one Hermes instance. Before deploying, always verify token uniqueness across all environments.'}",
    "sop_title": "SOP: Unknown",
    "automation": true
  }
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **57.0** / 100 (F) |
| Evidence | 5.0 / 20 |
| Impact | 16 / 20 |
| Reuse | 10.0 / 20 |
| Confidence | 16.0 / 20 |
| Actionability | 10.0 / 20 |
| Updated | 2026-06-11T16:07:25.734174+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `1c497f1c-5938-40c9-83fc-c51efc84ddb9`
