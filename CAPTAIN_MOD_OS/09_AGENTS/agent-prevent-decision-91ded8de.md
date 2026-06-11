---
schema: agent
table: agent_memory_registry
id: 02269066-d0d5-4e7b-9e96-0cf05be0b438
agent: Captain Mod
memory_type: constraint
key: prevent-decision-91ded8de
created: 2026-06-11T16:06:15.871695+00:00
updated: 2026-06-11T16:06:15.871695+00:00
quality_score: 57.2
quality_grade: F
---

# 🤖 Captain Mod — prevent-decision-91ded8de

## Metadata

| Field | Value |
|---|---|
| ID | `02269066-d0d5-4e7b-9e96-0cf05be0b438` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-decision-91ded8de` |
| Confidence | 0.85 |
| Source | enrichment-engine-decision |
| Created | 2026-06-11T16:06:15.871695+00:00 |
| Updated | 2026-06-11T16:06:15.871695+00:00 |

## Value

{
  "source_id": "91ded8de-78d1-4ad1-919e-c3876fc1c4dd",
  "enrichment": {
    "rule": "Decision rule: When technical decision needed, consider . Expected: Chose PostgreSQL for ACID compliance and JSONB support",
    "sop_title": "SOP: Unknown",
    "automation": true
  },
  "source_schema": "decision",
  "preventive_rule": "Decision rule: When technical decision needed, consider . Expected: Chose PostgreSQL for ACID compliance and JSONB support"
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **57.2** / 100 (F) |
| Evidence | 7.0 / 20 |
| Impact | 16 / 20 |
| Reuse | 10.0 / 20 |
| Confidence | 14.2 / 20 |
| Actionability | 10.0 / 20 |
| Updated | 2026-06-11T16:12:06.403263+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `02269066-d0d5-4e7b-9e96-0cf05be0b438`
