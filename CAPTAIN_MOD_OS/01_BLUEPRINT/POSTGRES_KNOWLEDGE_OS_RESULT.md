# POSTGRES_KNOWLEDGE_OS_RESULT

**Date:** 2026-06-11 15:05:46 UTC
**Status:** PASS

## Evidence

| Check | Result |
|---|---|
| PostgreSQL Version | 17.10 (Alpine) |
| Database Name | knowledge_os |
| Container | knowledge-os-postgres |
| Port | 127.0.0.1:5432 |
| Health | healthy |
| Persistence | /opt/data/postgres (Docker volume mount) |
| Restart Survived | YES |

## Schemas (8)

knowledge, decision, failure, lesson, research, project, audit, agent

## Roles (3)

| Role | Login |
|---|---|
| knowledge_admin | YES |
| knowledge_reader | YES |
| knowledge_writer | YES |

## Backup Strategy

- pg_dump verified: PASS
- Schema-only export tested
- Daily backup strategy: ready for cron setup

## Performance

| Metric | Value |
|---|---|
| RAM Usage | 27MB / 7.75GB (0.34%) |
| CPU | 0.41% |
| max_connections | 100 |
| Active connections | 6 |
| shared_buffers | 128MB |
| work_mem | 4MB |
| wal_level | replica |
| Disk free | 80.2GB (84%) |

## Container Config

- Auto-restart: unless-stopped
- Health check: pg_isready every 10s
- Data mount: /opt/data/postgres:/var/lib/postgresql/data
- Network: localhost only (127.0.0.1:5432)
