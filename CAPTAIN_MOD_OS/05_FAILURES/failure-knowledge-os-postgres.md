---
schema: failure
table: failure_registry
id: 007f20ed-5a10-4259-85ad-4a90b7794116
system: knowledge-os-postgres
failure_type: infrastructure
severity: high
status: resolved
created: 2026-06-11T15:38:54.997218+00:00
---

# ❌ knowledge-os-postgres — infrastructure

## Metadata

| Field | Value |
|---|---|
| ID | `007f20ed-5a10-4259-85ad-4a90b7794116` |
| System | knowledge-os-postgres |
| Type | infrastructure |
| Severity | high |
| Date | 2026-06-11T15:38:54.997218+00:00 |
| Status | resolved |
| Created | 2026-06-11T15:38:54.997218+00:00 |

## Symptom

PostgreSQL container unreachable from Hermes container

## Root Cause

{"text": "PostgreSQL on default bridge network, Hermes on hermes-workspace_default. Cross-network TCP blocked by Docker firewall."}

## Evidence

```json
{}
```

## Fix Applied

Connected PostgreSQL container to hermes-workspace_default network

## Verification



## Preventive Rule



## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `007f20ed-5a10-4259-85ad-4a90b7794116`
