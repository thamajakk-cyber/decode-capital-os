---
schema: agent
table: agent_memory_registry
id: 2dbd93c6-d90c-4cd1-a2e5-38a59c6199b8
agent: Captain Mod
memory_type: constraint
key: prevent-dashboard-loopback-bind
created: 2026-06-11T15:45:56.133833+00:00
updated: 2026-06-11T15:45:56.133833+00:00
quality_score: 47.0
quality_grade: F
---

# 🤖 Captain Mod — prevent-dashboard-loopback-bind

## Metadata

| Field | Value |
|---|---|
| ID | `2dbd93c6-d90c-4cd1-a2e5-38a59c6199b8` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-dashboard-loopback-bind` |
| Confidence | 1.00 |
| Source | rcaf-engine |
| Created | 2026-06-11T15:45:56.133833+00:00 |
| Updated | 2026-06-11T15:45:56.133833+00:00 |

## Value

{
  "fix_summary": "Added HERMES_DASHBOARD_HOST=0.0.0.0 and HERMES_DASHBOARD_INSECURE=1 to workspace .env",
  "preventive_rule": "Docker dashboard must bind to 0.0.0.0 not 127.0.0.1. Use HERMES_DASHBOARD_INSECURE=1 for non-loopback.",
  "root_cause_summary": "Dashboard s6 script defaults HERMES_DASHBOARD_HOST to 127.0.0.1 inside container. Workspace container cannot reach loopback. /api/sessions returns 500 causing .map() crash."
}

## Quality Score

| Metric | Score |
|---|---|
| Total | **47.0** / 100 (F) |
| Evidence | 5.0 / 20 |
| Impact | 16 / 20 |
| Reuse | 6.0 / 20 |
| Confidence | 14.0 / 20 |
| Actionability | 6.0 / 20 |
| Updated | 2026-06-11T15:52:45.584562+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `2dbd93c6-d90c-4cd1-a2e5-38a59c6199b8`
