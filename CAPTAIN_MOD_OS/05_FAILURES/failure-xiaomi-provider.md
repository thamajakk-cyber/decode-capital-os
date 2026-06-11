---
schema: failure
table: failure_registry
id: d072a0b6-075b-46bf-8dbe-e6a40bbc6f86
system: xiaomi-provider
failure_type: infrastructure
severity: medium
status: resolved
created: 2026-06-11T15:45:49.786660+00:00
quality_score: 59.0
quality_grade: F
---

# ❌ xiaomi-provider — infrastructure

## Metadata

| Field | Value |
|---|---|
| ID | `d072a0b6-075b-46bf-8dbe-e6a40bbc6f86` |
| System | xiaomi-provider |
| Type | infrastructure |
| Severity | medium |
| Date | 2026-06-11T15:45:49.786660+00:00 |
| Status | resolved |
| Created | 2026-06-11T15:45:49.786660+00:00 |

## Symptom

Invalid API key error when calling Xiaomi mimo-v2.5 provider through Hermes gateway [Evidence: 3 refs. Context: Status: resolved. Fix applied: Yes.]

## Root Cause

{"text": "Gateway API_SERVER_KEY auth layer rejecting unauthenticated requests. Xiaomi provider key was valid but gateway required its own [REDACTED]"}

## Evidence

```json
{}
```

## Fix Applied

No provider fix needed. Authenticated requests with proper API_SERVER_KEY bypass gateway auth.

## Verification

Direct Anthropic SDK test from container returned HTTP 200 with valid response

## Preventive Rule

Always authenticate through gateway API_SERVER_KEY when making provider requests

## Quality Score

| Metric | Score |
|---|---|
| Total | **59.0** / 100 (F) |
| Evidence | 9.0 / 20 |
| Impact | 10 / 20 |
| Reuse | 15.0 / 20 |
| Confidence | 8.0 / 20 |
| Actionability | 17.0 / 20 |
| Updated | 2026-06-11T16:12:06.392409+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `d072a0b6-075b-46bf-8dbe-e6a40bbc6f86`
