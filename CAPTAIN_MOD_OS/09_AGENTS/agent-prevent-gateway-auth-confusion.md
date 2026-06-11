---
schema: agent
table: agent_memory_registry
id: fd3fecd3-25cc-4d10-a2b4-ecd13095755b
agent: Captain Mod
memory_type: constraint
key: prevent-gateway-auth-confusion
created: 2026-06-11T15:45:49.803919+00:00
updated: 2026-06-11T15:45:49.803919+00:00
---

# 🤖 Captain Mod — prevent-gateway-auth-confusion

## Metadata

| Field | Value |
|---|---|
| ID | `fd3fecd3-25cc-4d10-a2b4-ecd13095755b` |
| Agent | Captain Mod |
| Memory Type | constraint |
| Key | `prevent-gateway-auth-confusion` |
| Confidence | 1.00 |
| Source | rcaf-engine |
| Created | 2026-06-11T15:45:49.803919+00:00 |
| Updated | 2026-06-11T15:45:49.803919+00:00 |

## Value

{
  "fix_summary": "No provider fix needed. Authenticated requests with proper API_SERVER_KEY bypass gateway auth.",
  "preventive_rule": "Always authenticate through gateway API_SERVER_KEY when making provider requests",
  "root_cause_summary": "Gateway API_SERVER_KEY auth layer rejecting unauthenticated requests. Xiaomi provider key was valid but gateway required its own [REDACTED]"
}

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `fd3fecd3-25cc-4d10-a2b4-ecd13095755b`
