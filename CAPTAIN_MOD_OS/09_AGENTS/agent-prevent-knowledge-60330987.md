---
schema: agent
table: agent_memory_registry
id: ab194116-fa2e-4c09-bbac-cdee4a5ffe09
agent: Captain Mod
memory_type: constraint
key: prevent-knowledge-60330987
created: 2026-06-11T16:06:15.866908+00:00
updated: 2026-06-11T16:06:15.866908+00:00
quality_score: 56.6
quality_grade: F
---

# 🤖 Captain Mod — prevent-knowledge-60330987

## Metadata

| Field | Value |
|---|---|
| ID | `ab194116-fa2e-4c09-bbac-cdee4a5ffe09` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-knowledge-60330987` |
| Confidence | 0.80 |
| Source | enrichment-engine-knowledge |
| Created | 2026-06-11T16:06:15.866908+00:00 |
| Updated | 2026-06-11T16:06:15.866908+00:00 |

## Value

{
  "source_id": "60330987-f865-4373-9a01-1ddff1fbe3c1",
  "enrichment": {
    "rule": "Rule from knowledge: Docker-based workspace with agent, dashboard, PostgreSQL",
    "sop_title": "SOP: Unknown",
    "automation": true
  },
  "source_schema": "knowledge",
  "preventive_rule": "Rule from knowledge: Docker-based workspace with agent, dashboard, PostgreSQL"
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **56.6** / 100 (F) |
| Evidence | 7.0 / 20 |
| Impact | 16 / 20 |
| Reuse | 10.0 / 20 |
| Confidence | 13.6 / 20 |
| Actionability | 10.0 / 20 |
| Updated | 2026-06-11T16:07:25.736536+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `ab194116-fa2e-4c09-bbac-cdee4a5ffe09`
