---
schema: lesson
table: lesson_registry
id: 0d7381bb-3608-401f-89e8-d02cfc58e6c8
title: Lesson: PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace
lesson_type: operational
created: 2026-06-11T15:43:07.426189+00:00
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

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `0d7381bb-3608-401f-89e8-d02cfc58e6c8`
