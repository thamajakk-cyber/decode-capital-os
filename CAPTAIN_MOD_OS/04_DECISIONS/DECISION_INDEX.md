---
type: index
schema: decision
table: decision_registry
project: Captain Mod OS
created: 2026-06-11
---

# ⚖️ Decision Index

## PostgreSQL Mapping

- **Schema**: `decision`
- **Table**: `decision.decision_registry`
- **Connection**: via Hermes Bridge

## Fields

| Field | Type | Description |
|---|---|---|
| `decision_key` | TEXT | Unique identifier |
| `category` | TEXT | Decision category |
| `decision_type` | TEXT | Type of decision |
| `title` | TEXT | Decision title |
| `description` | TEXT | Full description |
| `rationale` | TEXT | Why this decision was made |
| `alternatives_considered` | JSONB | Other options evaluated |
| `outcome` | TEXT | Decision outcome |
| `confidence_score` | FLOAT | Confidence (0-1) |
| `source` | TEXT | Origin source |
| `tags` | TEXT[] | Array of tags |

## Seeded Entries

| Key | Title | Outcome | Confidence |
|---|---|---|---|
| `hermes_workspace_installation` | Install Hermes Workspace via Docker Compose | successful_deployment | 1.0 |

## How to Add

### From PostgreSQL

```sql
INSERT INTO decision.decision_registry (decision_key, category, decision_type, title, description, rationale, alternatives_considered, outcome, confidence_score, source, tags)
VALUES ('key', 'category', 'type', 'Title', 'Description', 'Rationale', '{"alt1": "desc"}', 'outcome', 1.0, 'source', ARRAY['tag']);
```

## Index Pages

- [[HOME]] — Back to home
- [[LESSON_INDEX]] — Lessons from decisions
- [[FAILURE_INDEX]] — Failures from decisions
