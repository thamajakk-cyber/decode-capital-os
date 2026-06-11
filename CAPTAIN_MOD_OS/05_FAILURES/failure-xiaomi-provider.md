---
schema: failure
table: failure_registry
id: d072a0b6-075b-46bf-8dbe-e6a40bbc6f86
system: xiaomi-provider
failure_type: infrastructure
severity: medium
status: resolved
created: 2026-06-11T15:45:49.786660+00:00
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

Invalid API key error when calling Xiaomi mimo-v2.5 provider through Hermes gateway

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

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `d072a0b6-075b-46bf-8dbe-e6a40bbc6f86`
