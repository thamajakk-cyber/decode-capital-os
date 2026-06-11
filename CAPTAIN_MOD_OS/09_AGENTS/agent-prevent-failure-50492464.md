---
schema: agent
table: agent_memory_registry
id: 93f3f839-3a27-42fb-91b6-481100ad5fbc
agent: Captain Mod
memory_type: workflow
key: prevent-failure-50492464
created: 2026-06-11T16:07:41.207057+00:00
updated: 2026-06-11T16:07:41.207057+00:00
quality_score: 32.4
quality_grade: F
---

# 🤖 Captain Mod — prevent-failure-50492464

## Metadata

| Field | Value |
|---|---|
| ID | `93f3f839-3a27-42fb-91b6-481100ad5fbc` |
| Agent | Captain Mod |
| Memory Type | workflow |
| Key | `prevent-failure-50492464` |
| Confidence | 0.95 |
| Source | enrichment-engine-failure |
| Created | 2026-06-11T16:07:41.207057+00:00 |
| Updated | 2026-06-11T16:07:41.207057+00:00 |

## Value

{
  "source_id": "50492464-24ad-41d0-9d58-96cd1eab43f8",
  "source_schema": "failure",
  "preventive_rule": "Prevention for nginx-ssl: Always configure certbot auto-renewal. Monitor certificate expiry at 30-day intervals."
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **32.4** / 100 (F) |
| Evidence | 7.0 / 20 |
| Impact | 12 / 20 |
| Reuse | 0.0 / 20 |
| Confidence | 13.4 / 20 |
| Actionability | 0.0 / 20 |
| Updated | 2026-06-11T16:12:06.413192+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `93f3f839-3a27-42fb-91b6-481100ad5fbc`
