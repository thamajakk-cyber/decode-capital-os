---
schema: agent
table: agent_memory_registry
id: 5fc5b389-0128-4c2e-9b06-1c6ae7845c4a
agent: Captain Mod
memory_type: constraint
key: prevent-failure-b679752c
created: 2026-06-11T16:06:49.525202+00:00
updated: 2026-06-11T16:06:49.525202+00:00
quality_score: 50.4
quality_grade: F
---

# 🤖 Captain Mod — prevent-failure-b679752c

## Metadata

| Field | Value |
|---|---|
| ID | `5fc5b389-0128-4c2e-9b06-1c6ae7845c4a` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-failure-b679752c` |
| Confidence | 0.95 |
| Source | enrichment-engine-failure |
| Created | 2026-06-11T16:06:49.525202+00:00 |
| Updated | 2026-06-11T16:06:49.525202+00:00 |

## Value

{
  "source_id": "b679752c-cff8-4315-b38c-a741626055bf",
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
| Updated | 2026-06-11T16:07:25.738112+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `5fc5b389-0128-4c2e-9b06-1c6ae7845c4a`
