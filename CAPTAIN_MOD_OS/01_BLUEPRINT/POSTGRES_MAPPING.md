---
type: mapping
project: Captain Mod OS
database: knowledge_os
created: 2026-06-11
---

# 🔗 PostgreSQL ↔ Obsidian Mapping

## Database

- **Database**: `knowledge_os`
- **Container**: `knowledge-os-postgres`
- **PostgreSQL**: 17.10
- **Port**: 127.0.0.1:5432 (not exposed externally)
- **Bridge Network**: `hermes-workspace_default`

## Roles

| Role | Permissions | Use |
|---|---|---|
| `knowledge_admin` | ALL on knowledge_os | Full access |
| `knowledge_reader` | SELECT on all schemas | Read-only |
| `knowledge_writer` | INSERT, UPDATE on all schemas | Write access |

## Schema → Folder Mapping

| Schema | PostgreSQL Table | Obsidian Folder | Index Page |
|---|---|---|---|
| `knowledge` | `knowledge.knowledge_registry` | `02_KNOWLEDGE/` | [[KNOWLEDGE_INDEX]] |
| `decision` | `decision.decision_registry` | `04_DECISIONS/` | [[DECISION_INDEX]] |
| `failure` | `failure.failure_registry` | `05_FAILURES/` | [[FAILURE_INDEX]] |
| `lesson` | `lesson.lesson_registry` | `03_LESSONS/` | [[LESSON_INDEX]] |
| `agent` | `agent.agent_memory_registry` | `09_AGENTS/` | [[AGENT_INDEX]] |
| `research` | (future tables) | `06_RESEARCH/` | — |
| `project` | (future tables) | `07_PROJECTS/` | — |
| `audit` | (future tables) | `audits/` | — |

## Foreign Key Graph

```
lesson.lesson_registry
  ├── related_failure_id → failure.failure_registry(id)
  └── related_decision_id → decision.decision_registry(id)
```

## Connection String (from Hermes container)

```
postgresql://knowledge_admin:<password>@knowledge-os-postgres:5432/knowledge_os
```

> ⚠️ Actual password stored at `/opt/data/secrets/postgres.env` (chmod 600)

## Query Examples

### List all knowledge entries
```sql
SELECT knowledge_key, domain, category, confidence_score
FROM knowledge.knowledge_registry
ORDER BY created_at DESC;
```

### List all agent memories
```sql
SELECT agent_name, memory_type, memory_key, LEFT(memory_value, 50)
FROM agent.agent_memory_registry
ORDER BY created_at DESC;
```

### Find lessons linked to failures
```sql
SELECT l.title, f.title AS failure_title
FROM lesson.lesson_registry l
JOIN failure.failure_registry f ON l.related_failure_id = f.id;
```

### Get provider configuration
```sql
SELECT memory_value
FROM agent.agent_memory_registry
WHERE memory_type = 'configuration'
  AND memory_key = 'primary_provider';
```

## Seed Data Summary

| Schema | Table | Row Count |
|---|---|---|
| `knowledge` | `knowledge_registry` | 1 |
| `decision` | `decision_registry` | 1 |
| `failure` | `failure_registry` | 1 |
| `lesson` | `lesson_registry` | 1 |
| `agent` | `agent_memory_registry` | 3 |
| **Total** | | **7** |

## Bridge Verification

- Host → PostgreSQL: ✅ `pg_isready` accepts connections
- Hermes Container → PostgreSQL: ✅ TCP connect to `knowledge-os-postgres:5432`
- Read Test: ✅ All 5 tables readable
- Write Test: ✅ INSERT + SELECT verified (commit `28db8c3`)
- Persistence: ✅ Records survive container restart
- Security: ✅ No secrets in git or reports

## Related Documents

- [[MASTER_BLUEPRINT]] — Full architecture
- [[HOME]] — Navigation hub
- Audits: `KNOWLEDGE_BRIDGE_*.md` in `/root/decode-capital-os/audits/`
