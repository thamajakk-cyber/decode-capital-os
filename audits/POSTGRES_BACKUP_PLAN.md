# POSTGRES_BACKUP_PLAN

**Date:** 2026-06-11 15:05:46 UTC
**Status:** READY

## Backup Strategy

### Daily Backup (to be added to cron)

```bash
docker exec knowledge-os-postgres pg_dump -U knowledge_admin knowledge_os > /opt/data/postgres/backup_$(date +%Y%m%d).sql
```

### Retention

- Keep 7 daily backups
- Rotate oldest on new backup

### Restore Test Command

```bash
cat backup_YYYYMMDD.sql | docker exec -i knowledge-os-postgres psql -U knowledge_admin -d knowledge_os
```

### Current Backup Location

- /opt/data/postgres/ (persistent Docker mount)
- Container internal: /tmp/test_backup.sql (test only)
