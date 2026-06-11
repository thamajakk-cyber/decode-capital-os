# KNOWLEDGE_BRIDGE_SECRET_REPORT

**Date:** 2026-06-11 15:18:27 UTC
**Status:** PASS

## Secret Locations

| File | Status | Permissions |
|---|---|---|
| /opt/data/secrets/postgres.env | PRESENT | 600 |
| /opt/hermes-workspace/.env (POSTGRES_*) | PRESENT | 600 |

## Required Variables

| Variable | Present |
|---|---|
| POSTGRES_HOST | YES |
| POSTGRES_PORT | YES |
| POSTGRES_DB | YES |
| POSTGRES_USER | YES |
| POSTGRES_PASSWORD | YES |

## Injection Method

compose environment section in docker-compose.yml passes POSTGRES_* vars to hermes-agent container.
