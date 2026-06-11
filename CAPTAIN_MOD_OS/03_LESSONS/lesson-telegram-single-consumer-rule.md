---
schema: lesson
table: lesson_registry
id: 5109e76a-1213-4e2c-ae09-4b0c19a2bf4d
title: Telegram Single Consumer Rule
lesson_type: operational
created: 2026-06-11T15:45:33.879245+00:00
quality_score: 47.0
quality_grade: F
---

# 📖 Telegram Single Consumer Rule

## Metadata

| Field | Value |
|---|---|
| ID | `5109e76a-1213-4e2c-ae09-4b0c19a2bf4d` |
| Title | Telegram Single Consumer Rule |
| Type | operational |
| Date | 2026-06-11 |
| Confidence | 1.00 |
| Related Failure | `231e38f8-94dd-4422-8fd2-b33f3b657650` |
| Related Decision | `None` |
| Created | 2026-06-11T15:45:33.879245+00:00 |

## Summary

What: One Telegram bot [REDACTED] active consumer. Verify token uniqueness before deploying.. Why: Lesson recorded from operational experience. Learned: {'root_cause': 'Host Hermes and Docker Hermes both configured with same TELEGRAM_BOT_TOKEN', 'fix_ap

## Key Takeaways

```json
{
  "root_cause": "Host Hermes and Docker Hermes both configured with same TELEGRAM_BOT_TOKEN",
  "fix_applied": "Commented TELEGRAM_BOT_TOKEN in Docker agent .env file",
  "verification": "Verified Docker agent no longer polls Telegram. Host Hermes sole consumer confirmed.",
  "preventive_rule": "One Telegram bot token = One active consumer. Verify token uniqueness before deploying."
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
| Updated | 2026-06-11T16:07:25.729341+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `5109e76a-1213-4e2c-ae09-4b0c19a2bf4d`
