# KNOWLEDGE_BRIDGE_CONNECTIVITY_AUDIT

**Date:** 2026-06-11 15:18:27 UTC
**Status:** PASS

## Host → PostgreSQL

| Check | Result |
|---|---|
| Container healthy | knowledge-os-postgres: healthy |
| Port 5432 | accepting connections |
| Database exists | knowledge_os |
| Tables exist | 5 tables |
| Roles exist | 3 roles |

## Hermes Container → PostgreSQL

| Check | Result |
|---|---|
| DNS resolution | knowledge-os-postgres → 172.18.0.4 |
| TCP connect | PASS |
| psycopg2 installed | 2.9.12 (via uv) |
| SELECT from all 5 tables | PASS |

## Network

PostgreSQL connected to hermes-workspace_default network for inter-container communication.
