---
schema: lesson
table: lesson_registry
id: e08d1cbe-ee51-4262-b9e0-48b4f9c48668
title: One Bot Token = One Active Consumer
lesson_type: operational
created: 2026-06-11T15:07:49.841401+00:00
quality_score: 45.4
quality_grade: F
---

# 📖 One Bot Token = One Active Consumer

## Metadata

| Field | Value |
|---|---|
| ID | `e08d1cbe-ee51-4262-b9e0-48b4f9c48668` |
| Title | One Bot Token = One Active Consumer |
| Type | operational |
| Date | 2026-06-11 |
| Confidence | 0.95 |
| Related Failure | `b783c5ce-9c36-4a53-b973-18e2ec10b5b9` |
| Related Decision | `None` |
| Created | 2026-06-11T15:07:49.841401+00:00 |

## Summary

What: Telegram bot tokens can only be polled by one instance at a time. Running multiple Hermes instances . Why: Lesson recorded from operational experience. Learned: ['Never share bot tokens across instances', 'Disable Telegram in secondary instances', 'Use separate

## Key Takeaways

```json
[
  "Never share bot tokens across instances",
  "Disable Telegram in secondary instances",
  "Use separate bots for separate instances",
  "Always verify platform status after multi-instance deployment"
]
```

## Quality Score

| Metric | Score |
|---|---|
| Total | **45.4** / 100 (F) |
| Evidence | 5.0 / 20 |
| Impact | 17 / 20 |
| Reuse | 7.0 / 20 |
| Confidence | 13.4 / 20 |
| Actionability | 3.0 / 20 |
| Updated | 2026-06-11T16:12:06.394849+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `e08d1cbe-ee51-4262-b9e0-48b4f9c48668`
