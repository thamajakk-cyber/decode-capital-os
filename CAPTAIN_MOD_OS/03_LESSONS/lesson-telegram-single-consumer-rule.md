---
schema: lesson
table: lesson_registry
id: 7307933c-4e34-4991-bfc9-8304a8d0afb9
title: Telegram Single Consumer Rule
lesson_type: operational
created: 2026-06-11T15:39:32.179853+00:00
---

# 📖 Telegram Single Consumer Rule

## Metadata

| Field | Value |
|---|---|
| ID | `7307933c-4e34-4991-bfc9-8304a8d0afb9` |
| Title | Telegram Single Consumer Rule |
| Type | operational |
| Date | 2026-06-11 |
| Confidence | 1.00 |
| Related Failure | `b0d58855-d455-4155-9436-7c2099a3f5d4` |
| Related Decision | `None` |
| Created | 2026-06-11T15:39:32.179853+00:00 |

## Summary

One bot token must have exactly one active consumer at all times

## Key Takeaways

```json
{
  "rule": "One Telegram bot token = One active consumer",
  "checklist": [
    "Check .env files",
    "Check docker-compose.yml",
    "Check systemd services"
  ],
  "prevention": "Before starting any Hermes instance, verify no other instance uses the same token"
}
```

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `7307933c-4e34-4991-bfc9-8304a8d0afb9`
