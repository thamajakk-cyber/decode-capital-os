---
type: index
schema: knowledge
table: knowledge_registry
project: Captain Mod OS
created: 2026-06-11
---

# 📚 Knowledge Index

## PostgreSQL Mapping

- **Schema**: `knowledge`
- **Table**: `knowledge.knowledge_registry`
- **Connection**: via Hermes Bridge

## Fields

| Field | Type | Description |
|---|---|---|
| `knowledge_key` | TEXT | Unique identifier |
| `domain` | TEXT | Domain classification |
| `category` | TEXT | Category within domain |
| `knowledge_type` | TEXT | Type of knowledge |
| `content` | TEXT | Knowledge content |
| `confidence_score` | FLOAT | Confidence level (0-1) |
| `source` | TEXT | Source of knowledge |
| `tags` | TEXT[] | Array of tags |
| `metadata` | JSONB | Extended metadata |

## Knowledge Entries

### Seeded Entries

| Key | Domain | Category | Confidence |
|---|---|---|---|
| `decode_capital_os_blueprint` | system_architecture | blueprint | 1.0 |

## How to Add

### From Obsidian

Create a new `.md` file in this folder with frontmatter matching the PostgreSQL schema.

### From PostgreSQL

```sql
INSERT INTO knowledge.knowledge_registry (knowledge_key, domain, category, knowledge_type, content, confidence_score, source, tags)
VALUES ('new_knowledge', 'domain', 'category', 'type', 'content', 1.0, 'source', ARRAY['tag1']);
```

### From Hermes Bridge

```
hermes execute: python3 -c "
import psycopg2
conn = psycopg2.connect('postgresql://knowledge_admin:***@knowledge-os-postgres:5432/knowledge_os')
..."
```

## Index Pages

- [[HOME]] — Back to home
- [[MASTER_BLUEPRINT]] — System architecture
- [[POSTGRES_MAPPING]] — Full database mapping
