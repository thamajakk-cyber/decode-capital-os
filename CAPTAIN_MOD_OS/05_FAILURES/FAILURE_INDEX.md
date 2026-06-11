---
type: index
schema: failure
table: failure_registry
project: Captain Mod OS
created: 2026-06-11
---

# ❌ Failure Index

## PostgreSQL Mapping

- **Schema**: `failure`
- **Table**: `failure.failure_registry`
- **Connection**: via Hermes Bridge

## Fields

| Field | Type | Description |
|---|---|---|
| `failure_key` | TEXT | Unique identifier |
| `category` | TEXT | Failure category |
| `failure_type` | TEXT | Type of failure |
| `severity` | TEXT | Severity level |
| `title` | TEXT | Failure title |
| `description` | TEXT | Full description |
| `root_cause` | TEXT | Root cause analysis |
| `impact` | TEXT | Impact assessment |
| `resolution` | TEXT | How it was resolved |
| `resolved` | BOOLEAN | Is it resolved? |
| `confidence_score` | FLOAT | Confidence (0-1) |
| `source` | TEXT | Origin source |
| `tags` | TEXT[] | Array of tags |

## Seeded Entries

| Key | Title | Severity | Resolved | Confidence |
|---|---|---|---|---|
| `telegram_polling_conflict` | Two Hermes instances sharing one bot token | high | ✅ true | 1.0 |

## How to Add

### From PostgreSQL

```sql
INSERT INTO failure.failure_registry (failure_key, category, failure_type, severity, title, description, root_cause, impact, resolution, resolved, confidence_score, source, tags)
VALUES ('key', 'category', 'type', 'high', 'Title', 'Description', 'Root cause', 'Impact', 'Resolution', true, 1.0, 'source', ARRAY['tag']);
```

## Index Pages

- [[HOME]] — Back to home
- [[LESSON_INDEX]] — Lessons from failures
- [[DECISION_INDEX]] — Related decisions
