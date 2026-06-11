---
schema: lesson
table: lesson_registry
id: 0d7381bb-3608-401f-89e8-d02cfc58e6c8
title: Lesson: PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace
lesson_type: operational
created: 2026-06-11T15:43:07.426189+00:00
quality_score: 45.0
quality_grade: F
---

# 📖 Lesson: PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace

## Metadata

| Field | Value |
|---|---|
| ID | `0d7381bb-3608-401f-89e8-d02cfc58e6c8` |
| Title | Lesson: PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace |
| Type | operational |
| Date | 2026-06-11 |
| Confidence | 1.00 |
| Related Failure | `9b32e356-b4bc-40ad-b657-92fa8404486a` |
| Related Decision | `None` |
| Created | 2026-06-11T15:43:07.426189+00:00 |

## Summary

Prevention for: PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace_default network. Docker firewall blocks cross-network TCP.

## Key Takeaways

```json
{
  "rule": "Always verify configuration",
  "prevention": "Always declare shared networks in docker-compose.yml for inter-container communication",
  "root_cause": "PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace_default network. Docker firewall blocks cross-network TCP."
}
```

## Quality Score

| Metric | Score |
|---|---|
| Total | **45.0** / 100 (F) |
| Evidence | 5.0 / 20 |
| Impact | 18 / 20 |
| Reuse | 7.0 / 20 |
| Confidence | 12.0 / 20 |
| Actionability | 3.0 / 20 |
| Updated | 2026-06-11T15:52:45.578232+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `0d7381bb-3608-401f-89e8-d02cfc58e6c8`
