---
type: index
schema: agent
table: agent_memory_registry
project: Captain Mod OS
created: 2026-06-11
---

# 🤖 Agent Memory Index

## PostgreSQL Mapping

- **Schema**: `agent`
- **Table**: `agent.agent_memory_registry`
- **Connection**: via Hermes Bridge

## Fields

| Field | Type | Description |
|---|---|---|
| `agent_name` | TEXT | Agent identifier |
| `memory_type` | TEXT | Type of memory (see constraints) |
| `memory_key` | TEXT | Unique key for this memory |
| `memory_value` | TEXT | Memory content |
| `context` | TEXT | Context information |
| `confidence_score` | FLOAT | Confidence (0-1) |
| `source` | TEXT | Origin source |
| `tags` | TEXT[] | Array of tags |
| `metadata` | JSONB | Extended metadata |

## Allowed Memory Types

```
capability · preference · observation · lesson · strategy
configuration · status · context · decision · summary
```

## Seeded Entries

| Agent | Type | Key | Value | Confidence |
|---|---|---|---|---|
| Captain Mod | configuration | primary_provider | provider: xiaomi, model: mimo-v2.5 | 1.0 |
| Captain Mod | strategy | startup_sequence | 1. gateway 2. telegram 3. dashboard 4. workspace | 1.0 |
| Hermes Workspace | capability | bridge_test | Hermes successfully wrote to PostgreSQL Knowledge OS | 1.0 |

## How to Add

### From PostgreSQL

```sql
INSERT INTO agent.agent_memory_registry (agent_name, memory_type, memory_key, memory_value, context, confidence_score, source, tags)
VALUES ('Agent Name', 'capability', 'memory_key', 'memory_value', 'context', 1.0, 'source', ARRAY['tag']);
```

### Read Provider Config

```sql
SELECT memory_value FROM agent.agent_memory_registry
WHERE memory_type = 'configuration' AND memory_key = 'primary_provider';
```

## Index Pages

- [[HOME]] — Back to home
- [[KNOWLEDGE_INDEX]] — Knowledge registry
- [[MASTER_BLUEPRINT]] — System architecture
