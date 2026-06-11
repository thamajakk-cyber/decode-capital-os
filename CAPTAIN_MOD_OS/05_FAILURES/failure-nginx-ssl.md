---
schema: failure
table: failure_registry
id: 50492464-24ad-41d0-9d58-96cd1eab43f8
system: nginx-ssl
failure_type: configuration
severity: high
status: resolved
created: 2026-06-11T16:07:40.983533+00:00
quality_score: 62.0
quality_grade: D
---

# ❌ nginx-ssl — configuration

## Metadata

| Field | Value |
|---|---|
| ID | `50492464-24ad-41d0-9d58-96cd1eab43f8` |
| System | nginx-ssl |
| Type | configuration |
| Severity | high |
| Date | 2026-06-11T16:07:40.983533+00:00 |
| Status | resolved |
| Created | 2026-06-11T16:07:40.983533+00:00 |

## Symptom

SSL certificate nearing expiry within 90 days [Evidence: 3 refs. Context: Status: resolved. Fix applied: Yes.]

## Root Cause

{"text": "Let's Encrypt certificate auto-renewal not configured"}

## Evidence

```json
{}
```

## Fix Applied

Added certbot cron job for automatic renewal every 60 days

## Verification

SSL certificate expiry extended. Auto-renewal cron verified.

## Preventive Rule

Always configure certbot auto-renewal. Monitor certificate expiry at 30-day intervals.

## Quality Score

| Metric | Score |
|---|---|
| Total | **62.0** / 100 (D) |
| Evidence | 9.0 / 20 |
| Impact | 15 / 20 |
| Reuse | 15.0 / 20 |
| Confidence | 6.0 / 20 |
| Actionability | 17.0 / 20 |
| Updated | 2026-06-11T16:07:41.209463+00:00 |

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `50492464-24ad-41d0-9d58-96cd1eab43f8`
