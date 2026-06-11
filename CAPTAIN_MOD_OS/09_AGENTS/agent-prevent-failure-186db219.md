---
schema: agent
table: agent_memory_registry
id: 473dddbf-af50-413a-9744-2d8da25e91d6
agent: Captain Mod
memory_type: constraint
key: prevent-failure-186db219
created: 2026-06-11T16:06:49.530723+00:00
updated: 2026-06-11T16:06:49.530723+00:00
quality_score: 50.4
quality_grade: F
---

# 🤖 Captain Mod — prevent-failure-186db219

## Metadata

| Field | Value |
|---|---|
| ID | `473dddbf-af50-413a-9744-2d8da25e91d6` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-failure-186db219` |
| Confidence | 0.95 |
| Source | enrichment-engine-failure |
| Created | 2026-06-11T16:06:49.530723+00:00 |
| Updated | 2026-06-11T16:06:49.530723+00:00 |

## Value

{
  "source_id": "186db219-88eb-4ff5-870e-c1298d4dbae5",
  "source_schema": "failure",
  "preventive_rule": "Prevention for nginx: After container recreation, verify nginx upstream targets match new container ports"
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
| Updated | 2026-06-11T16:12:06.405285+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `473dddbf-af50-413a-9744-2d8da25e91d6`
