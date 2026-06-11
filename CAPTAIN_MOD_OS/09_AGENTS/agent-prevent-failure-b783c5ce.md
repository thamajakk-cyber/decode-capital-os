---
schema: agent
table: agent_memory_registry
id: 66800657-4f47-42e0-be93-8311e94e8256
agent: Captain Mod
memory_type: constraint
key: prevent-failure-b783c5ce
created: 2026-06-11T16:06:49.538182+00:00
updated: 2026-06-11T16:06:49.538182+00:00
quality_score: 50.4
quality_grade: F
---

# 🤖 Captain Mod — prevent-failure-b783c5ce

## Metadata

| Field | Value |
|---|---|
| ID | `66800657-4f47-42e0-be93-8311e94e8256` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-failure-b783c5ce` |
| Confidence | 0.95 |
| Source | enrichment-engine-failure |
| Created | 2026-06-11T16:06:49.538182+00:00 |
| Updated | 2026-06-11T16:06:49.538182+00:00 |

## Value

{
  "source_id": "b783c5ce-9c36-4a53-b973-18e2ec10b5b9",
  "source_schema": "failure",
  "preventive_rule": "Prevention for hermes-workspace-telegram: One bot [REDACTED] active consumer. If multiple Hermes instances exist, disable Telegram in all but one."
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
| Updated | 2026-06-11T16:12:06.406121+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `66800657-4f47-42e0-be93-8311e94e8256`
