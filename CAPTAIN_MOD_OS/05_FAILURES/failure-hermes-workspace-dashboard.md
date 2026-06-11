---
schema: failure
table: failure_registry
id: fcdf248d-2df3-4a16-99c7-750b71ea40d9
system: hermes-workspace-dashboard
failure_type: infrastructure
severity: high
status: resolved
created: 2026-06-11T15:45:56.116452+00:00
quality_score: 62.0
quality_grade: D
---

# ❌ hermes-workspace-dashboard — infrastructure

## Metadata

| Field | Value |
|---|---|
| ID | `fcdf248d-2df3-4a16-99c7-750b71ea40d9` |
| System | hermes-workspace-dashboard |
| Type | infrastructure |
| Severity | high |
| Date | 2026-06-11T15:45:56.116452+00:00 |
| Status | resolved |
| Created | 2026-06-11T15:45:56.116452+00:00 |

## Symptom

Dashboard frontend crashes with Cannot read properties of undefined reading map when loading sessions sidebar

## Root Cause

{"text": "Dashboard s6 script defaults HERMES_DASHBOARD_HOST to 127.0.0.1 inside container. Workspace container cannot reach loopback. /api/sessions returns 500 causing .map() crash."}

## Evidence

```json
{}
```

## Fix Applied

Added HERMES_DASHBOARD_HOST=0.0.0.0 and HERMES_DASHBOARD_INSECURE=1 to workspace .env

## Verification

Sessions sidebar loads successfully. All 9 sessions visible. No .map() crash in console.

## Preventive Rule

Docker dashboard must bind to 0.0.0.0 not 127.0.0.1. Use HERMES_DASHBOARD_INSECURE=1 for non-loopback.

## Quality Score

| Metric | Score |
|---|---|
| Total | **62.0** / 100 (D) |
| Evidence | 9.0 / 20 |
| Impact | 15 / 20 |
| Reuse | 15.0 / 20 |
| Confidence | 6.0 / 20 |
| Actionability | 17.0 / 20 |
| Updated | 2026-06-11T15:52:45.575415+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `fcdf248d-2df3-4a16-99c7-750b71ea40d9`
