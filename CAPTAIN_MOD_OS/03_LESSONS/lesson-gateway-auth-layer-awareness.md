---
schema: lesson
table: lesson_registry
id: 55af0d68-9399-458d-b508-d136c5f64158
title: Gateway Auth Layer Awareness
lesson_type: operational
created: 2026-06-11T15:45:49.794776+00:00
quality_score: 45.0
quality_grade: F
---

# 📖 Gateway Auth Layer Awareness

## Metadata

| Field | Value |
|---|---|
| ID | `55af0d68-9399-458d-b508-d136c5f64158` |
| Title | Gateway Auth Layer Awareness |
| Type | operational |
| Date | 2026-06-11 |
| Confidence | 1.00 |
| Related Failure | `d072a0b6-075b-46bf-8dbe-e6a40bbc6f86` |
| Related Decision | `None` |
| Created | 2026-06-11T15:45:49.794776+00:00 |

## Summary

Always authenticate through gateway API_SERVER_KEY when making provider requests

## Key Takeaways

```json
{
  "root_cause": "Gateway API_SERVER_KEY auth layer rejecting unauthenticated requests. Xiaomi provider key was valid but gateway required its own Bearer token.",
  "fix_applied": "No provider fix needed. Authenticated requests with proper API_SERVER_KEY bypass gateway auth.",
  "verification": "Direct Anthropic SDK test from container returned HTTP 200 with valid response",
  "preventive_rule": "Always authenticate through gateway API_SERVER_KEY when making provider requests"
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
| Updated | 2026-06-11T15:52:45.579163+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `55af0d68-9399-458d-b508-d136c5f64158`
