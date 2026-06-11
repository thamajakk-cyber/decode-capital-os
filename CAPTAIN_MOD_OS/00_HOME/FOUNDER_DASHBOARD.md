---
type: dashboard
project: Captain Mod OS
created: 2026-06-11
---

# 📊 Founder Dashboard — Captain Mod OS

## Executive Overview

| Metric | Score | Grade |
|---|---|---|
| **Overall Health** | 91.7 | **A** |
| Knowledge Health | 80.1 | B |
| Governance Score | 99.0 | A+ |
| Automation Score | 96.0 | A+ |

## System Status

| Metric | Value |
|---|---|
| Total Records | 76 |
| Curated Assets | 32 |
| Principles | 13 |
| Policies | 7 |
| Rules | 12 |
| SOPs | 15 |
| Open Contradictions | 0 |
| Resolved Contradictions | 5 |

## Knowledge Intelligence

| Registry | Count | Avg Quality |
|---|---|---|
| Knowledge | 2 | 53.2 |
| Decisions | 2 | 23.0 |
| Failures | 10 | 60.1 |
| Lessons | 10 | 46.0 |
| Agent Memories | 52 | 50.2 |

## RCAF Activity

| Metric | Value |
|---|---|
| Total Failures | 10 |
| Resolved | 9 (90%) |
| Open | 0 |
| Lessons Generated | 10 |
| Preventive Rules | 47 |

## Governance Center

| Asset | Count |
|---|---|
| Organizational Principles | 13 |
| Policies | 7 |
| Canonical Rules | 12 |
| Core SOPs | 15 |

## Top Knowledge Assets

1. hermes-workspace-telegram — 68.0 (D)
2. nginx — 64.0 (D)
3. knowledge-os-postgres — 64.0 (D)
4. hermes-workspace-dashboard — 64.0 (D)
5. nginx-ssl — 62.0 (D)

## Dashboard Refresh

```bash
# Refresh materialized views
python3 scripts/dashboard_api.py --refresh

# Populate metrics
python3 scripts/dashboard_api.py --populate

# View all metrics
python3 scripts/dashboard_api.py --metrics
```
