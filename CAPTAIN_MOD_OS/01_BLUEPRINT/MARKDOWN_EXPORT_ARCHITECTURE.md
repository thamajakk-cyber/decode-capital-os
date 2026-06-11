---
type: architecture
project: Captain Mod OS
component: markdown_exporter
version: 1.0.0
created: 2026-06-11
---

# 📤 PostgreSQL → Obsidian Markdown Export Architecture

## Overview

Automated exporter that reads PostgreSQL `knowledge_os` database and generates Obsidian-compatible Markdown files. PostgreSQL remains **Source of Truth**. Obsidian becomes **Human Knowledge Interface**.

## Data Flow

```
PostgreSQL (Source of Truth)
    ↓
export_to_obsidian.py (Exporter)
    ↓
Markdown Files (Human Interface)
    ↓
CAPTAIN_MOD_OS/ (Obsidian Vault)
```

## Schema → Folder Mapping

| Schema | Table | Vault Folder | Slug Pattern |
|---|---|---|---|
| `knowledge` | `knowledge_registry` | `02_KNOWLEDGE/` | `knowledge-{key}.md` |
| `decision` | `decision_registry` | `04_DECISIONS/` | `decision-{key}.md` |
| `failure` | `failure_registry` | `05_FAILURES/` | `failure-{key}.md` |
| `lesson` | `lesson_registry` | `03_LESSONS/` | `lesson-{key}.md` |
| `agent` | `agent_memory_registry` | `09_AGENTS/` | `agent-{name}-{key}.md` |

## Markdown Template

Each exported file follows:

```markdown
---
schema: {schema}
table: {table}
id: {uuid}
key: {record_key}
created: {created_at}
updated: {updated_at}
tags: [{tags}]
---

# {title}

## Metadata

| Field | Value |
|---|---|
| ID | {uuid} |
| Key | {record_key} |
| Created | {created_at} |
| Updated | {updated_at} |
| Source | {source} |
| Confidence | {confidence_score} |

## Content

{content}

## Source PostgreSQL

- Database: knowledge_os
- Schema: {schema}
- Table: {table}
- Row: {uuid}
```

## Export Modes

| Mode | Behavior | Use Case |
|---|---|---|
| `full` | Export all records | Initial sync, recovery |
| `incremental` | Export records updated since last run | Scheduled automation |

## Security Rules

1. **Never export**: passwords, tokens, API keys, secrets
2. **Sanitize**: any field matching secret patterns → `[REDACTED]`
3. **No secrets in filenames**
4. **No environment variables in output**

## Dependencies

- `psycopg2` (installed in Hermes container via uv)
- Python 3.11+
- PostgreSQL 17.10 (existing)
