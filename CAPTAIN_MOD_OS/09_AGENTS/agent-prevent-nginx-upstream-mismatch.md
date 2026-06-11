---
schema: agent
table: agent_memory_registry
id: 49107fcc-5870-4345-be7d-700184671cb8
agent: Captain Mod
memory_type: constraint
key: prevent-nginx-upstream-mismatch
created: 2026-06-11T15:56:35.972542+00:00
updated: 2026-06-11T15:56:35.972542+00:00
quality_score: 0
quality_grade: F
---

# 🤖 Captain Mod — prevent-nginx-upstream-mismatch

## Metadata

| Field | Value |
|---|---|
| ID | `49107fcc-5870-4345-be7d-700184671cb8` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-nginx-upstream-mismatch` |
| Confidence | 1.00 |
| Source | rcaf-engine |
| Created | 2026-06-11T15:56:35.972542+00:00 |
| Updated | 2026-06-11T15:56:35.972542+00:00 |

## Value

{
  "fix_summary": "Updated nginx proxy_pass to correct container hostname:port",
  "preventive_rule": "After container recreation, verify nginx upstream targets match new container ports",
  "root_cause_summary": "nginx upstream pointing to wrong container port after recreation"
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **0** / 100 (F) |
| Evidence | 0 / 20 |
| Impact | 0 / 20 |
| Reuse | 0 / 20 |
| Confidence | 0 / 20 |
| Actionability | 0 / 20 |
| Updated | None |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `49107fcc-5870-4345-be7d-700184671cb8`
