---
schema: lesson
table: lesson_registry
id: 8533a92e-ecfd-46be-8f27-d57bf3fab30d
title: Docker Compose Network Planning
lesson_type: operational
created: 2026-06-11T15:45:43.506758+00:00
quality_score: 47.0
quality_grade: F
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

What: Always declare shared networks in docker-compose.yml for inter-container communication. Why: Lesson recorded from operational experience. Learned: {'root_cause': 'PostgreSQL on default bridge network, Hermes on hermes-workspace_default. Docker fir

## Key Takeaways

```json
{
  "root_cause": "PostgreSQL on default bridge network, Hermes on hermes-workspace_default. Docker firewall blocks cross-network TCP.",
  "fix_applied": "Connected PostgreSQL container to hermes-workspace_default via docker network connect",
  "verification": "TCP connect to knowledge-os-postgres:5432 returns success from Hermes container",
  "preventive_rule": "Always declare shared networks in docker-compose.yml for inter-container communication"
}
```

## Quality Score

| Metric | Score |
|---|---|
| Total | **47.0** / 100 (F) |
| Evidence | 5.0 / 20 |
| Impact | 18 / 20 |
| Reuse | 7.0 / 20 |
| Confidence | 14.0 / 20 |
| Actionability | 3.0 / 20 |
| Updated | 2026-06-11T16:12:06.396081+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `8533a92e-ecfd-46be-8f27-d57bf3fab30d`
