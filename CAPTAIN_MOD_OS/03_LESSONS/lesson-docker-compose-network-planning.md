---
schema: lesson
table: lesson_registry
id: 8533a92e-ecfd-46be-8f27-d57bf3fab30d
title: Docker Compose Network Planning
lesson_type: operational
created: 2026-06-11T15:45:43.506758+00:00
---

# 📖 Docker Compose Network Planning

## Metadata

| Field | Value |
|---|---|
| ID | `8533a92e-ecfd-46be-8f27-d57bf3fab30d` |
| Title | Docker Compose Network Planning |
| Type | operational |
| Date | 2026-06-11 |
| Confidence | 1.00 |
| Related Failure | `b679752c-cff8-4315-b38c-a741626055bf` |
| Related Decision | `None` |
| Created | 2026-06-11T15:45:43.506758+00:00 |

## Summary

Always declare shared networks in docker-compose.yml for inter-container communication

## Key Takeaways

```json
{
  "root_cause": "PostgreSQL on default bridge network, Hermes on hermes-workspace_default. Docker firewall blocks cross-network TCP.",
  "fix_applied": "Connected PostgreSQL container to hermes-workspace_default via docker network connect",
  "verification": "TCP connect to knowledge-os-postgres:5432 returns success from Hermes container",
  "preventive_rule": "Always declare shared networks in docker-compose.yml for inter-container communication"
}
```

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `8533a92e-ecfd-46be-8f27-d57bf3fab30d`
