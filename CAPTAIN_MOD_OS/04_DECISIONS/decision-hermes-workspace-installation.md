---
schema: decision
table: decision_registry
id: a243c55a-0f8b-4b47-af96-94ab6dc11553
title: Hermes Workspace Installation
decision_type: technical
status: validated
created: 2026-06-11T15:07:49.841401+00:00
---

# ⚖️ Hermes Workspace Installation

## Metadata

| Field | Value |
|---|---|
| ID | `a243c55a-0f8b-4b47-af96-94ab6dc11553` |
| Title | Hermes Workspace Installation |
| Type | technical |
| Date | 2026-06-11 |
| Status | validated |
| Created By | founder |
| Created | 2026-06-11T15:07:49.841401+00:00 |

## Context

Need central AI workspace for Captain Mod operations with provider integration and web UI.

## Reasoning

Docker-based deployment provides isolation, persistence, and easy management. GitHub MCP integration enables code operations.

## Chosen Option

Docker Compose deployment on VPS with nginx reverse proxy and Let Encrypt SSL.

## Alternatives

```json
[
  "Install bare metal",
  "Use cloud PaaS",
  "Docker Compose deployment"
]
```

## Expected Outcome

Fully operational workspace with provider, MCP, and Telegram integration.

## Actual Outcome

Operational PASS. All gates passed. Frontend error resolved. Telegram conflict resolved.

## Source

- Database: `knowledge_os`
- Schema: `decision`
- Table: `decision_registry`
- Row: `a243c55a-0f8b-4b47-af96-94ab6dc11553`
