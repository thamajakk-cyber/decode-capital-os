---
schema: failure
table: failure_registry
id: 186db219-88eb-4ff5-870e-c1298d4dbae5
system: nginx
failure_type: infrastructure
severity: high
status: resolved
created: 2026-06-11T15:56:35.953924+00:00
quality_score: 64.0
quality_grade: D
---

# ❌ nginx — infrastructure

## Metadata

| Field | Value |
|---|---|
| ID | `186db219-88eb-4ff5-870e-c1298d4dbae5` |
| System | nginx |
| Type | infrastructure |
| Severity | high |
| Date | 2026-06-11T15:56:35.953924+00:00 |
| Status | resolved |
| Created | 2026-06-11T15:56:35.953924+00:00 |

## Symptom

nginx reverse proxy returning 502 Bad Gateway for workspace UI [Evidence: 3 refs. Context: Status: resolved. Fix applied: Yes.]

## Root Cause

{"text": "nginx upstream pointing to wrong container port after recreation"}

## Evidence

```json
{}
```

## Fix Applied

Updated nginx proxy_pass to correct container hostname:port

## Verification

https://decodecapital.tech returns 200 OK with full workspace UI

## Preventive Rule

After container recreation, verify nginx upstream targets match new container ports

## Quality Score

| Metric | Score |
|---|---|
| Total | **64.0** / 100 (D) |
| Evidence | 9.0 / 20 |
| Impact | 15 / 20 |
| Reuse | 15.0 / 20 |
| Confidence | 8.0 / 20 |
| Actionability | 17.0 / 20 |
| Updated | 2026-06-11T16:07:25.726647+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `186db219-88eb-4ff5-870e-c1298d4dbae5`
