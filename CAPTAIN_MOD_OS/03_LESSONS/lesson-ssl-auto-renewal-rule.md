---
schema: lesson
table: lesson_registry
id: 86b56ccb-3c20-4516-b8d7-ec5397995f64
title: SSL Auto-Renewal Rule
lesson_type: operational
created: 2026-06-11T16:07:40.991452+00:00
quality_score: 45.0
quality_grade: F
---

# 📖 SSL Auto-Renewal Rule

## Metadata

| Field | Value |
|---|---|
| ID | `86b56ccb-3c20-4516-b8d7-ec5397995f64` |
| Title | SSL Auto-Renewal Rule |
| Type | operational |
| Date | 2026-06-11 |
| Confidence | 1.00 |
| Related Failure | `50492464-24ad-41d0-9d58-96cd1eab43f8` |
| Related Decision | `None` |
| Created | 2026-06-11T16:07:40.991452+00:00 |

## Summary

Always configure certbot auto-renewal. Monitor certificate expiry at 30-day intervals.

## Key Takeaways

```json
{
  "root_cause": "Let's Encrypt certificate auto-renewal not configured",
  "fix_applied": "Added certbot cron job for automatic renewal every 60 days",
  "verification": "SSL certificate expiry extended. Auto-renewal cron verified.",
  "preventive_rule": "Always configure certbot auto-renewal. Monitor certificate expiry at 30-day intervals."
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
| Updated | 2026-06-11T16:12:06.397273+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `86b56ccb-3c20-4516-b8d7-ec5397995f64`
