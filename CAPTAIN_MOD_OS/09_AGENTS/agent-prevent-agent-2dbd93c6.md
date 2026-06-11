---
schema: agent
table: agent_memory_registry
id: 98aab1ca-8257-40c5-89d7-acada3985237
agent: Captain Mod
memory_type: constraint
key: prevent-agent-2dbd93c6
created: 2026-06-11T16:06:49.607640+00:00
updated: 2026-06-11T16:06:49.607640+00:00
quality_score: 51.0
quality_grade: F
---

# 🤖 Captain Mod — prevent-agent-2dbd93c6

## Metadata

| Field | Value |
|---|---|
| ID | `98aab1ca-8257-40c5-89d7-acada3985237` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-agent-2dbd93c6` |
| Confidence | 1.00 |
| Source | enrichment-engine-agent |
| Created | 2026-06-11T16:06:49.607640+00:00 |
| Updated | 2026-06-11T16:06:49.607640+00:00 |

## Value

{
  "source_id": "2dbd93c6-d90c-4cd1-a2e5-38a59c6199b8",
  "source_schema": "agent",
  "preventive_rule": "Docker dashboard must bind to 0.0.0.0 not 127.0.0.1. Use HERMES_DASHBOARD_INSECURE=1 for non-loopback."
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
| Updated | 2026-06-11T16:07:25.744591+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `98aab1ca-8257-40c5-89d7-acada3985237`
