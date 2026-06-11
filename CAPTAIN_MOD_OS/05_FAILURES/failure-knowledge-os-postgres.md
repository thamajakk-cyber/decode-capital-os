---
schema: failure
table: failure_registry
id: 9b32e356-b4bc-40ad-b657-92fa8404486a
system: knowledge-os-postgres
failure_type: application
severity: high
status: resolved
created: 2026-06-11T15:43:07.419398+00:00
---

# ❌ knowledge-os-postgres — application

## Metadata

| Field | Value |
|---|---|
| ID | `9b32e356-b4bc-40ad-b657-92fa8404486a` |
| System | knowledge-os-postgres |
| Type | application |
| Severity | high |
| Date | 2026-06-11T15:43:07.419398+00:00 |
| Status | resolved |
| Created | 2026-06-11T15:43:07.419398+00:00 |

## Symptom

PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace_default network. Docker firewall blocks cross-network TCP.

## Root Cause

{"text": "PostgreSQL container on default bridge network unreachable from Hermes container on hermes-workspace_default network. Docker firewall blocks cross-network TCP."}

## Evidence

```json
{}
```

## Fix Applied

Connected PostgreSQL container to hermes-workspace_default via docker network connect

## Verification



## Preventive Rule

Always declare shared networks in docker-compose.yml for inter-container communication

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `9b32e356-b4bc-40ad-b657-92fa8404486a`
