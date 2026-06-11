---
schema: agent
table: agent_memory_registry
id: bfd54e46-5f0c-41b0-afc1-1aebe68e41ab
agent: Captain Mod
memory_type: constraint
key: prevent-agent-fb0619b3
created: 2026-06-11T16:06:49.598153+00:00
updated: 2026-06-11T16:06:49.598153+00:00
quality_score: 51.0
quality_grade: F
---

# 🤖 Captain Mod — prevent-agent-fb0619b3

## Metadata

| Field | Value |
|---|---|
| ID | `bfd54e46-5f0c-41b0-afc1-1aebe68e41ab` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-agent-fb0619b3` |
| Confidence | 1.00 |
| Source | enrichment-engine-agent |
| Created | 2026-06-11T16:06:49.598153+00:00 |
| Updated | 2026-06-11T16:06:49.598153+00:00 |

## Value

{
  "source_id": "fb0619b3-3951-41af-bb10-f1f46e06580e",
  "source_schema": "agent",
  "preventive_rule": "{'text': 'Verified: Hermes Workspace can INSERT, SELECT, UPDATE records across all 5 registry tables via psycopg2 bridge.'}"
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
| Updated | 2026-06-11T16:07:25.743985+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `bfd54e46-5f0c-41b0-afc1-1aebe68e41ab`
