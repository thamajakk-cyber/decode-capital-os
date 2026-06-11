---
schema: agent
table: agent_memory_registry
id: 7b649fbc-58e9-406d-8bc9-2896ce7b5ce6
agent: Captain Mod
memory_type: constraint
key: lesson-postgresql-container-on-default-bridge-network-unreachable-f
created: 2026-06-11T15:43:07.433451+00:00
updated: 2026-06-11T15:43:07.433451+00:00
quality_score: 47.0
quality_grade: F
---

# 🤖 Captain Mod — lesson-postgresql-container-on-default-bridge-network-unreachable-f

## Metadata

| Field | Value |
|---|---|
| ID | `7b649fbc-58e9-406d-8bc9-2896ce7b5ce6` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `lesson-postgresql-container-on-default-bridge-network-unreachable-f` |
| Confidence | 1.00 |
| Source | capture-automation-test |
| Created | 2026-06-11T15:43:07.433451+00:00 |
| Updated | 2026-06-11T15:43:07.433451+00:00 |

## Value

{
  "text": "Lesson learned from: PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace_default network. Docker firewall blocks cross-network TCP.. Prevention: Always declare shared networks in docker-compose.yml for inter-container communication"
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
| Updated | 2026-06-11T15:52:45.583259+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `7b649fbc-58e9-406d-8bc9-2896ce7b5ce6`
