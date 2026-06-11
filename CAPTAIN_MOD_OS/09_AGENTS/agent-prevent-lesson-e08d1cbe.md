---
schema: agent
table: agent_memory_registry
id: 3a6c2817-c276-4b77-a1b1-9d0378b77d60
agent: Captain Mod
memory_type: constraint
key: prevent-lesson-e08d1cbe
created: 2026-06-11T16:06:49.547030+00:00
updated: 2026-06-11T16:06:49.547030+00:00
quality_score: 50.4
quality_grade: F
---

# 🤖 Captain Mod — prevent-lesson-e08d1cbe

## Metadata

| Field | Value |
|---|---|
| ID | `3a6c2817-c276-4b77-a1b1-9d0378b77d60` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-lesson-e08d1cbe` |
| Confidence | 0.95 |
| Source | enrichment-engine-lesson |
| Created | 2026-06-11T16:06:49.547030+00:00 |
| Updated | 2026-06-11T16:06:49.547030+00:00 |

## Value

{
  "source_id": "e08d1cbe-ee51-4262-b9e0-48b4f9c48668",
  "source_schema": "lesson",
  "preventive_rule": "['Never share bot tokens across instances', 'Disable Telegram in secondary instances', 'Use separate bots for separate instances', 'Always verify platform status after multi-instance deployment']"
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
| Updated | 2026-06-11T16:12:06.407108+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `3a6c2817-c276-4b77-a1b1-9d0378b77d60`
