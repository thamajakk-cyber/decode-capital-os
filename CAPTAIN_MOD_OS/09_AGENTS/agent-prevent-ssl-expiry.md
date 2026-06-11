---
schema: agent
table: agent_memory_registry
id: 84e6c72a-f341-4740-a941-347f37b7a6da
agent: Captain Mod
memory_type: constraint
key: prevent-ssl-expiry
created: 2026-06-11T16:07:40.999811+00:00
updated: 2026-06-11T16:07:40.999811+00:00
quality_score: 49.0
quality_grade: F
---

# 🤖 Captain Mod — prevent-ssl-expiry

## Metadata

| Field | Value |
|---|---|
| ID | `84e6c72a-f341-4740-a941-347f37b7a6da` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-ssl-expiry` |
| Confidence | 1.00 |
| Source | rcaf-engine |
| Created | 2026-06-11T16:07:40.999811+00:00 |
| Updated | 2026-06-11T16:07:40.999811+00:00 |

## Value

{
  "fix_summary": "Added certbot cron job for automatic renewal every 60 days",
  "preventive_rule": "Always configure certbot auto-renewal. Monitor certificate expiry at 30-day intervals.",
  "root_cause_summary": "Let's Encrypt certificate auto-renewal not configured"
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **49.0** / 100 (F) |
| Evidence | 7.0 / 20 |
| Impact | 16 / 20 |
| Reuse | 6.0 / 20 |
| Confidence | 14.0 / 20 |
| Actionability | 6.0 / 20 |
| Updated | 2026-06-11T16:12:06.413014+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `84e6c72a-f341-4740-a941-347f37b7a6da`
