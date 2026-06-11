---
schema: lesson
table: lesson_registry
id: 86db02d5-5406-41d6-a76f-0b8e62cbcc08
title: Nginx Upstream Verification After Recreation
lesson_type: operational
created: 2026-06-11T15:56:35.962784+00:00
quality_score: 0
quality_grade: F
---

# 📖 Nginx Upstream Verification After Recreation

## Metadata

| Field | Value |
|---|---|
| ID | `86db02d5-5406-41d6-a76f-0b8e62cbcc08` |
| Title | Nginx Upstream Verification After Recreation |
| Type | operational |
| Date | 2026-06-11 |
| Confidence | 1.00 |
| Related Failure | `186db219-88eb-4ff5-870e-c1298d4dbae5` |
| Related Decision | `None` |
| Created | 2026-06-11T15:56:35.962784+00:00 |

## Summary

After container recreation, verify nginx upstream targets match new container ports

## Key Takeaways

```json
{
  "root_cause": "nginx upstream pointing to wrong container port after recreation",
  "fix_applied": "Updated nginx proxy_pass to correct container hostname:port",
  "verification": "https://decodecapital.tech returns 200 OK with full workspace UI",
  "preventive_rule": "After container recreation, verify nginx upstream targets match new container ports"
}
```

## Quality Score

| Metric | Score |
|---|---|
| Total | **0** / 100 (F) |
| Evidence | 0 / 20 |
| Impact | 0 / 20 |
| Reuse | 0 / 20 |
| Confidence | 0 / 20 |
| Actionability | 0 / 20 |
| Updated | None |

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `86db02d5-5406-41d6-a76f-0b8e62cbcc08`
