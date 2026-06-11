# KNOWLEDGE_OS_CORE_TABLES_RESULT

**Date:** 2026-06-11 15:08:10 UTC
**Status:** PASS

## Tables Created (5)

| Schema | Table | Indexes | Records |
|---|---|---|---|
| knowledge | knowledge_registry | 7 | 1 |
| decision | decision_registry | 4 | 1 |
| failure | failure_registry | 5 | 1 |
| lesson | lesson_registry | 3 | 1 |
| agent | agent_memory_registry | 5 | 3 |

**Total:** 5 tables, 24 indexes, 7 seed records

## Constraints

- 2 Foreign Keys (lesson -> failure, lesson -> decision)
- CHECK constraints on all status/type/severity columns
- UNIQUE on knowledge.slug and agent (agent_name, memory_type, memory_key)
- UUID primary keys with gen_random_uuid()

## Seed Data

| Registry | Record |
|---|---|
| Knowledge | Captain Mod SMC Pro Max Master Blueprint |
| Decision | Hermes Workspace Installation |
| Failure | Telegram Polling Conflict |
| Lesson | One Bot Token = One Active Consumer (linked to failure) |
| Agent Memory | Primary Provider, Deployment, Telegram Constraint |

## Referential Integrity

Lesson -> Failure: VERIFIED (One Bot Token linked to hermes-workspace-telegram)

## Performance

- DB Size: 8MB
- Query Execution: 0.038ms (tag search)
- Connection: healthy
- Indexes: active
