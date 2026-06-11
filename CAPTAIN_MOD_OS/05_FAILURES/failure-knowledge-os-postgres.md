---
schema: failure
table: failure_registry
id: b679752c-cff8-4315-b38c-a741626055bf
system: knowledge-os-postgres
failure_type: infrastructure
severity: high
status: resolved
created: 2026-06-11T15:45:43.500222+00:00
quality_score: 62.0
quality_grade: D
---

# ❌ knowledge-os-postgres — infrastructure

## Metadata

| Field | Value |
|---|---|
| ID | `b679752c-cff8-4315-b38c-a741626055bf` |
| System | knowledge-os-postgres |
| Type | infrastructure |
| Severity | high |
| Date | 2026-06-11T15:45:43.500222+00:00 |
| Status | resolved |
| Created | 2026-06-11T15:45:43.500222+00:00 |

## Symptom

PostgreSQL container unreachable from Hermes container due to Docker bridge network isolation

## Root Cause

{"text": "PostgreSQL on default bridge network, Hermes on hermes-workspace_default. Docker firewall blocks cross-network TCP."}

## Evidence

```json
{}
```

## Fix Applied

Connected PostgreSQL container to hermes-workspace_default via docker network connect

## Verification

TCP connect to knowledge-os-postgres:5432 returns success from Hermes container

## Preventive Rule

Always declare shared networks in docker-compose.yml for inter-container communication

## Quality Score

| Metric | Score |
|---|---|
| Total | **62.0** / 100 (D) |
| Evidence | 9.0 / 20 |
| Impact | 15 / 20 |
| Reuse | 15.0 / 20 |
| Confidence | 6.0 / 20 |
| Actionability | 17.0 / 20 |
| Updated | 2026-06-11T15:52:45.574634+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `b679752c-cff8-4315-b38c-a741626055bf`
