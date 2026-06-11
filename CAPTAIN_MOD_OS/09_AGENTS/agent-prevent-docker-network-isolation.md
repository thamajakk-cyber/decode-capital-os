---
schema: agent
table: agent_memory_registry
id: 17f24f4f-2bd2-4afa-8432-436d6eb874e7
agent: Captain Mod
memory_type: constraint
key: prevent-docker-network-isolation
created: 2026-06-11T15:45:43.514418+00:00
updated: 2026-06-11T15:45:43.514418+00:00
quality_score: 59.0
quality_grade: F
---

# 🤖 Captain Mod — prevent-docker-network-isolation

## Metadata

| Field | Value |
|---|---|
| ID | `17f24f4f-2bd2-4afa-8432-436d6eb874e7` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-docker-network-isolation` |
| Confidence | 1.00 |
| Source | rcaf-engine |
| Created | 2026-06-11T15:45:43.514418+00:00 |
| Updated | 2026-06-11T15:45:43.514418+00:00 |

## Value

{
  "enrichment": {
    "rule": "Always declare shared networks in docker-compose.yml for inter-container communication",
    "sop_title": "SOP: Unknown",
    "automation": true
  },
  "fix_summary": "Connected PostgreSQL container to hermes-workspace_default via docker network connect",
  "preventive_rule": "Always declare shared networks in docker-compose.yml for inter-container communication",
  "root_cause_summary": "PostgreSQL on default bridge network, Hermes on hermes-workspace_default. Docker firewall blocks cross-network TCP."
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **59.0** / 100 (F) |
| Evidence | 7.0 / 20 |
| Impact | 16 / 20 |
| Reuse | 10.0 / 20 |
| Confidence | 16.0 / 20 |
| Actionability | 10.0 / 20 |
| Updated | 2026-06-11T16:12:06.401772+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `17f24f4f-2bd2-4afa-8432-436d6eb874e7`
