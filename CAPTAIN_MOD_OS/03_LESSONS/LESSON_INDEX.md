---
type: index
schema: lesson
table: lesson_registry
project: Captain Mod OS
created: 2026-06-11
---

# 📖 Lesson Index

## PostgreSQL Mapping

- **Schema**: `lesson`
- **Table**: `lesson.lesson_registry`
- **Connection**: via Hermes Bridge

## Fields

| Field | Type | Description |
|---|---|---|
| `lesson_key` | TEXT | Unique identifier |
| `category` | TEXT | Lesson category |
| `lesson_type` | TEXT | Type of lesson |
| `title` | TEXT | Lesson title |
| `description` | TEXT | Full description |
| `root_cause` | TEXT | Root cause analysis |
| `fix_applied` | TEXT | Fix that was applied |
| `prevention` | TEXT | Prevention strategy |
| `confidence_score` | FLOAT | Confidence (0-1) |
| `source` | TEXT | Origin source |
| `tags` | TEXT[] | Array of tags |
| `related_failure_id` | UUID | FK → failure_registry |
| `related_decision_id` | UUID | FK → decision_registry |

## Foreign Key Relationships

- `related_failure_id` → `failure.failure_registry(id)`
- `related_decision_id` → `decision.decision_registry(id)`

## Seeded Entries

| Key | Title | Linked Failure | Confidence |
|---|---|---|---|
| `hermes_telegram_conflict_resolution` | Never let two Hermes instances share one bot token | telegram_polling_conflict | 1.0 |

## How to Add

### From PostgreSQL

```sql
INSERT INTO lesson.lesson_registry (lesson_key, category, lesson_type, title, description, root_cause, fix_applied, prevention, confidence_score, source, tags, related_failure_id)
VALUES ('lesson_key', 'category', 'type', 'Title', 'Description', 'Root cause', 'Fix', 'Prevention', 1.0, 'source', ARRAY['tag'], '<failure_uuid>');
```

## Index Pages

- [[HOME]] — Back to home
- [[FAILURE_INDEX]] — Related failures
- [[DECISION_INDEX]] — Related decisions
