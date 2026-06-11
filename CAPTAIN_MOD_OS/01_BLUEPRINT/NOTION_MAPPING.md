# NOTION MAPPING — Captain Mod OS

**Architecture:**
PostgreSQL (Source of Truth) → Dashboard Metrics → Notion (Presentation Layer)

**Notion is Presentation Layer ONLY.** Notion never writes back to PostgreSQL.

---

## Database Mapping

### 1. Executive Dashboard

| Notion Field | PostgreSQL Source |
|---|---|
| Metric Name | `dashboard.dashboard_metrics.metric_name` |
| Metric Category | `dashboard.dashboard_metrics.metric_category` |
| Metric Value | `dashboard.dashboard_metrics.metric_value` |
| Health Grade | Calculated from metric_value |
| Status | Calculated from metric_value |
| Last Updated | `dashboard.dashboard_metrics.snapshot_time` |

### 2. Knowledge Assets

| Notion Field | PostgreSQL Source |
|---|---|
| Title | `knowledge.curated_assets.asset_name` |
| Category | `knowledge.curated_assets.category` |
| Quality Score | `knowledge.curated_assets.quality_score` |
| Quality Grade | Calculated from quality_score |
| Status | `knowledge.curated_assets.status` |
| Source Registry | Hardcoded: `curated_assets` |
| Created | `knowledge.curated_assets.created_at` |
| Updated | `knowledge.curated_assets.updated_at` |

### 3. RCAF Registry

| Notion Field | PostgreSQL Source |
|---|---|
| Name | Combined from source table |
| Type | Derived from source table |
| Severity | `failure.failure_registry.severity` (failures only) |
| Status | `{source_table}.status` |
| Quality Score | `{source_table}.quality_score` |
| Source Table | Identifies source table |
| Created | `{source_table}.created_at` |

**Source Tables:**
- `failure.failure_registry` → Type: Failure
- `lesson.lesson_registry` → Type: Lesson
- `agent.agent_memory_registry` (where memory_type='preventive_rule') → Type: Rule

### 4. Organizational Principles

| Notion Field | PostgreSQL Source |
|---|---|
| Name | Combined from source table |
| Type | Derived from source table |
| Quality Score | `{source_table}.quality_score` |
| Compliance | quality_score / 100 |
| Status | `{source_table}.status` |
| Description | Statement/objective text |
| Created | `{source_table}.created_at` |

**Source Tables:**
- `governance.organizational_principles` → Type: Principle
- `governance.policy_registry` → Type: Policy
- `governance.rule_registry` → Type: Rule
- `governance.sop_library` → Type: SOP

---

## Upsert Strategy

- **Key:** Title/Name field (stable, unique per record)
- **Create:** If title not found in Notion database
- **Update:** If title already exists in Notion database
- **No Delete:** Records are never deleted from Notion (append-only)

## Security Rules

- Notion API key stored in `/opt/data/secrets/notion.env` (chmod 600)
- No secrets written to Notion records
- No passwords, tokens, or API keys in any synced field
- Sync direction: PostgreSQL → Notion ONLY

## Refresh Strategy

Manual trigger:
```bash
python3 scripts/notion_sync.py --all
```

Selective sync:
```bash
python3 scripts/notion_sync.py --executive
python3 scripts/notion_sync.py --knowledge
python3 scripts/notion_sync.py --rcaf
python3 scripts/notion_sync.py --principles
```

Verification:
```bash
python3 scripts/notion_sync.py --verify
```
