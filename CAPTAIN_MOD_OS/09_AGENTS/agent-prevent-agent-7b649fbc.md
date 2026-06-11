---
schema: agent
table: agent_memory_registry
id: f1b9b6e7-b8f4-41ee-b0d9-88ac8dcd7b0d
agent: Captain Mod
memory_type: constraint
key: prevent-agent-7b649fbc
created: 2026-06-11T16:06:49.610287+00:00
updated: 2026-06-11T16:06:49.610287+00:00
quality_score: 51.0
quality_grade: F
---

# 🤖 Captain Mod — prevent-agent-7b649fbc

## Metadata

| Field | Value |
|---|---|
| ID | `f1b9b6e7-b8f4-41ee-b0d9-88ac8dcd7b0d` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-agent-7b649fbc` |
| Confidence | 1.00 |
| Source | enrichment-engine-agent |
| Created | 2026-06-11T16:06:49.610287+00:00 |
| Updated | 2026-06-11T16:06:49.610287+00:00 |

## Value

{
  "source_id": "7b649fbc-58e9-406d-8bc9-2896ce7b5ce6",
  "source_schema": "agent",
  "preventive_rule": "{'text': 'Lesson learned from: PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace_default network. Docker firewall blocks cross-network TCP.. Prevention: Always declare shared networks in docker-compose.yml for inter-container communication'}"
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
| Updated | 2026-06-11T16:07:25.744775+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `f1b9b6e7-b8f4-41ee-b0d9-88ac8dcd7b0d`
