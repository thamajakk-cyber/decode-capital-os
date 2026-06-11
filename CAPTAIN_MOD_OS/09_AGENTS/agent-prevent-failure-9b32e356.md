---
schema: agent
table: agent_memory_registry
id: 76e3bce6-9c56-4fb5-a61e-5f415fd210d9
agent: Captain Mod
memory_type: constraint
key: prevent-failure-9b32e356
created: 2026-06-11T16:06:49.519996+00:00
updated: 2026-06-11T16:06:49.519996+00:00
quality_score: 50.4
quality_grade: F
---

# 🤖 Captain Mod — prevent-failure-9b32e356

## Metadata

| Field | Value |
|---|---|
| ID | `76e3bce6-9c56-4fb5-a61e-5f415fd210d9` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-failure-9b32e356` |
| Confidence | 0.95 |
| Source | enrichment-engine-failure |
| Created | 2026-06-11T16:06:49.519996+00:00 |
| Updated | 2026-06-11T16:06:49.519996+00:00 |

## Value

{
  "source_id": "9b32e356-b4bc-40ad-b657-92fa8404486a",
  "source_schema": "failure",
  "preventive_rule": "Prevention for knowledge-os-postgres: Always declare shared networks in docker-compose.yml for inter-container communication"
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
| Updated | 2026-06-11T16:07:25.737561+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `76e3bce6-9c56-4fb5-a61e-5f415fd210d9`
