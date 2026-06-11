---
schema: lesson
table: lesson_registry
id: 93b35cb0-43ee-4c03-b853-6c62f52889eb
title: Docker Dashboard Binding Rule
lesson_type: operational
created: 2026-06-11T15:45:56.124939+00:00
quality_score: 47.0
quality_grade: F
---

# 📖 Docker Dashboard Binding Rule

## Metadata

| Field | Value |
|---|---|
| ID | `93b35cb0-43ee-4c03-b853-6c62f52889eb` |
| Title | Docker Dashboard Binding Rule |
| Type | operational |
| Date | 2026-06-11 |
| Confidence | 1.00 |
| Related Failure | `fcdf248d-2df3-4a16-99c7-750b71ea40d9` |
| Related Decision | `None` |
| Created | 2026-06-11T15:45:56.124939+00:00 |

## Summary

What: Docker dashboard must bind to 0.0.0.0 not 127.0.0.1. Use HERMES_DASHBOARD_INSECURE=1 for non-loopbac. Why: Lesson recorded from operational experience. Learned: {'root_cause': 'Dashboard s6 script defaults HERMES_DASHBOARD_HOST to 127.0.0.1 inside container. Wo

## Key Takeaways

```json
{
  "root_cause": "Dashboard s6 script defaults HERMES_DASHBOARD_HOST to 127.0.0.1 inside container. Workspace container cannot reach loopback. /api/sessions returns 500 causing .map() crash.",
  "fix_applied": "Added HERMES_DASHBOARD_HOST=0.0.0.0 and HERMES_DASHBOARD_INSECURE=1 to workspace .env",
  "verification": "Sessions sidebar loads successfully. All 9 sessions visible. No .map() crash in console.",
  "preventive_rule": "Docker dashboard must bind to 0.0.0.0 not 127.0.0.1. Use HERMES_DASHBOARD_INSECURE=1 for non-loopback."
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
| Updated | 2026-06-11T16:07:25.730097+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `93b35cb0-43ee-4c03-b853-6c62f52889eb`
