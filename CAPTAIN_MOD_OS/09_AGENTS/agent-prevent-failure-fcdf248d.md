---
schema: agent
table: agent_memory_registry
id: c52d9f2b-9d4a-4150-8770-eee20976a41b
agent: Captain Mod
memory_type: constraint
key: prevent-failure-fcdf248d
created: 2026-06-11T16:06:49.528062+00:00
updated: 2026-06-11T16:06:49.528062+00:00
quality_score: 50.4
quality_grade: F
---

# 🤖 Captain Mod — prevent-failure-fcdf248d

## Metadata

| Field | Value |
|---|---|
| ID | `c52d9f2b-9d4a-4150-8770-eee20976a41b` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-failure-fcdf248d` |
| Confidence | 0.95 |
| Source | enrichment-engine-failure |
| Created | 2026-06-11T16:06:49.528062+00:00 |
| Updated | 2026-06-11T16:06:49.528062+00:00 |

## Value

{
  "source_id": "fcdf248d-2df3-4a16-99c7-750b71ea40d9",
  "source_schema": "failure",
  "preventive_rule": "Prevention for hermes-workspace-dashboard: Docker dashboard must bind to 0.0.0.0 not 127.0.0.1. Use HERMES_DASHBOARD_INSECURE=1 for non-loopback."
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
| Updated | 2026-06-11T16:07:25.738388+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `c52d9f2b-9d4a-4150-8770-eee20976a41b`
