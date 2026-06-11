#!/usr/bin/env python3
"""
PostgreSQL → Obsidian Markdown Exporter
========================================
Reads knowledge_os database and generates Obsidian-compatible Markdown files.
PostgreSQL = Source of Truth. Obsidian = Human Knowledge Interface.

Usage:
    python3 export_to_obsidian.py --mode full
    python3 export_to_obsidian.py --mode incremental
    python3 export_to_obsidian.py --dry-run
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip3 install psycopg2-binary")
    sys.exit(1)

# ============================================================
# Configuration
# ============================================================

VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT", "/root/decode-capital-os/CAPTAIN_MOD_OS")
STATE_FILE = os.path.join(VAULT_ROOT, ".export_state.json")

DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "knowledge-os-postgres"),
    "port": int(os.environ.get("POSTGRES_PORT", "5432")),
    "dbname": os.environ.get("POSTGRES_DB", "knowledge_os"),
    "user": os.environ.get("POSTGRES_USER", "knowledge_admin"),
    "password": os.environ.get("POSTGRES_PASSWORD", ""),
}

# Schema → Folder mapping
SCHEMA_MAP = {
    "knowledge": {
        "table": "knowledge_registry",
        "folder": "02_KNOWLEDGE",
        "slug_prefix": "knowledge",
        "title_field": "title",
    },
    "decision": {
        "table": "decision_registry",
        "folder": "04_DECISIONS",
        "slug_prefix": "decision",
        "title_field": "title",
    },
    "failure": {
        "table": "failure_registry",
        "folder": "05_FAILURES",
        "slug_prefix": "failure",
        "title_field": "system_name",
    },
    "lesson": {
        "table": "lesson_registry",
        "folder": "03_LESSONS",
        "slug_prefix": "lesson",
        "title_field": "title",
    },
    "agent": {
        "table": "agent_memory_registry",
        "folder": "09_AGENTS",
        "slug_prefix": "agent",
        "title_field": "memory_key",
    },
}

# Secret patterns to redact
SECRET_PATTERNS = [
    r"(?i)password\s*[:=]\s*\S+",
    r"(?i)api[_-]?key\s*[:=]\s*\S+",
    r"(?i)token\s*[:=]\s*\S+",
    r"(?i)secret\s*[:=]\s*\S+",
    r"ghp_[A-Za-z0-9]+",
    r"github_pat_[A-Za-z0-9]+",
    r"Bearer\s+[A-Za-z0-9._-]+",
]


def redact_secrets(text) -> str:
    """Redact any secret patterns from text. Handles non-string types."""
    if text is None:
        return ""
    if isinstance(text, (dict, list)):
        text = json.dumps(text, indent=2, default=str)
    if not isinstance(text, str):
        text = str(text)
    for pattern in SECRET_PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text)
    return text


def slugify(text: str) -> str:
    """Convert text to filesystem-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:80].strip("-")


def fmt(val) -> str:
    """Format a value for display."""
    if val is None:
        return "N/A"
    if isinstance(val, bool):
        return "✅" if val else "❌"
    if isinstance(val, (dict, list)):
        return json.dumps(val, indent=2, default=str)
    return str(val)


def fmt_tags(tags) -> str:
    """Format tags for frontmatter."""
    if not tags:
        return "[]"
    if isinstance(tags, list):
        return "[" + ", ".join(tags) + "]"
    if isinstance(tags, str):
        return "[" + tags + "]"
    return "[]"


# ============================================================
# Template Generators (match actual DB column names)
# ============================================================

def generate_knowledge_md(row: dict) -> str:
    title = row.get("title", "Unknown")
    slug = row.get("slug", "unknown")
    category = row.get("category", "N/A")
    subcategory = row.get("subcategory", "N/A")
    content = redact_secrets(row.get("content"))
    summary = redact_secrets(row.get("summary"))
    source = row.get("source", "N/A")
    tags = fmt_tags(row.get("tags"))
    status = row.get("status", "N/A")
    confidence = row.get("confidence_score", "N/A")
    created = row.get("created_at", "N/A")
    updated = row.get("updated_at", "N/A")
    row_id = row.get("id", "N/A")

    q_score = row.get('quality_score', 0)
    q_grade = row.get('quality_grade', 'F')
    q_evidence = row.get('evidence_score', 0)
    q_impact = row.get('impact_score', 0)
    q_reuse = row.get('reuse_score', 0)
    q_conf = row.get('q_confidence_score', 0)
    q_action = row.get('actionability_score', 0)
    q_updated = row.get('quality_last_updated', 'N/A')

    return f"""---
schema: knowledge
table: knowledge_registry
id: {row_id}
slug: {slug}
category: {category}
created: {created}
updated: {updated}
tags: {tags}
quality_score: {q_score}
quality_grade: {q_grade}
---

# 📚 {title}

## Metadata

| Field | Value |
|---|---|
| ID | `{row_id}` |
| Slug | `{slug}` |
| Category | {category} |
| Subcategory | {subcategory} |
| Status | {status} |
| Confidence | {confidence} |
| Source | {source} |
| Created | {created} |
| Updated | {updated} |

## Summary

{summary}

## Content

{content}

## Tags

{tags}

## Quality Score

| Metric | Score |
|---|---|
| Total | **{q_score}** / 100 ({q_grade}) |
| Evidence | {q_evidence} / 20 |
| Impact | {q_impact} / 20 |
| Reuse | {q_reuse} / 20 |
| Confidence | {q_conf} / 20 |
| Actionability | {q_action} / 20 |
| Updated | {q_updated} |

## Source

- Database: `knowledge_os`
- Schema: `knowledge`
- Table: `knowledge_registry`
- Row: `{row_id}`
"""


def generate_decision_md(row: dict) -> str:
    title = row.get("title", "Unknown")
    decision_date = row.get("decision_date", "N/A")
    decision_type = row.get("decision_type", "N/A")
    context = redact_secrets(row.get("context"))
    reasoning = redact_secrets(row.get("reasoning"))
    alternatives = fmt(row.get("alternatives"))
    chosen_option = redact_secrets(row.get("chosen_option"))
    expected_outcome = redact_secrets(row.get("expected_outcome"))
    actual_outcome = redact_secrets(row.get("actual_outcome"))
    status = row.get("status", "N/A")
    created_by = row.get("created_by", "N/A")
    created = row.get("created_at", "N/A")
    row_id = row.get("id", "N/A")

    q_score = row.get('quality_score', 0)
    q_grade = row.get('quality_grade', 'F')
    q_evidence = row.get('evidence_score', 0)
    q_impact = row.get('impact_score', 0)
    q_reuse = row.get('reuse_score', 0)
    q_conf = row.get('q_confidence_score', 0)
    q_action = row.get('actionability_score', 0)
    q_updated = row.get('quality_last_updated', 'N/A')

    return f"""---
schema: decision
table: decision_registry
id: {row_id}
title: {title}
decision_type: {decision_type}
status: {status}
created: {created}
quality_score: {q_score}
quality_grade: {q_grade}
---

# ⚖️ {title}

## Metadata

| Field | Value |
|---|---|
| ID | `{row_id}` |
| Title | {title} |
| Type | {decision_type} |
| Date | {decision_date} |
| Status | {status} |
| Created By | {created_by} |
| Created | {created} |

## Context

{context}

## Reasoning

{reasoning}

## Chosen Option

{chosen_option}

## Alternatives

```json
{alternatives}
```

## Expected Outcome

{expected_outcome}

## Actual Outcome

{actual_outcome}

## Quality Score

| Metric | Score |
|---|---|
| Total | **{q_score}** / 100 ({q_grade}) |
| Evidence | {q_evidence} / 20 |
| Impact | {q_impact} / 20 |
| Reuse | {q_reuse} / 20 |
| Confidence | {q_conf} / 20 |
| Actionability | {q_action} / 20 |
| Updated | {q_updated} |

## Source

- Database: `knowledge_os`
- Schema: `decision`
- Table: `decision_registry`
- Row: `{row_id}`
"""


def generate_failure_md(row: dict) -> str:
    system_name = row.get("system_name", "Unknown")
    failure_date = row.get("failure_date", "N/A")
    failure_type = row.get("failure_type", "N/A")
    severity = row.get("severity", "N/A")
    symptom = redact_secrets(row.get("symptom"))
    root_cause = redact_secrets(row.get("root_cause"))
    evidence = fmt(row.get("evidence"))
    fix_applied = redact_secrets(row.get("fix_applied"))
    verification = redact_secrets(row.get("verification"))
    preventive_rule = redact_secrets(row.get("preventive_rule"))
    status = row.get("status", "N/A")
    created = row.get("created_at", "N/A")
    row_id = row.get("id", "N/A")

    q_score = row.get('quality_score', 0)
    q_grade = row.get('quality_grade', 'F')
    q_evidence = row.get('evidence_score', 0)
    q_impact = row.get('impact_score', 0)
    q_reuse = row.get('reuse_score', 0)
    q_conf = row.get('q_confidence_score', 0)
    q_action = row.get('actionability_score', 0)
    q_updated = row.get('quality_last_updated', 'N/A')

    return f"""---
schema: failure
table: failure_registry
id: {row_id}
system: {system_name}
failure_type: {failure_type}
severity: {severity}
status: {status}
created: {created}
quality_score: {q_score}
quality_grade: {q_grade}
---

# ❌ {system_name} — {failure_type}

## Metadata

| Field | Value |
|---|---|
| ID | `{row_id}` |
| System | {system_name} |
| Type | {failure_type} |
| Severity | {severity} |
| Date | {failure_date} |
| Status | {status} |
| Created | {created} |

## Symptom

{symptom}

## Root Cause

{root_cause}

## Evidence

```json
{evidence}
```

## Fix Applied

{fix_applied}

## Verification

{verification}

## Preventive Rule

{preventive_rule}

## Quality Score

| Metric | Score |
|---|---|
| Total | **{q_score}** / 100 ({q_grade}) |
| Evidence | {q_evidence} / 20 |
| Impact | {q_impact} / 20 |
| Reuse | {q_reuse} / 20 |
| Confidence | {q_conf} / 20 |
| Actionability | {q_action} / 20 |
| Updated | {q_updated} |

## Source

- Database: `knowledge_os`
- Schema: `failure`
- Table: `failure_registry`
- Row: `{row_id}`
"""


def generate_lesson_md(row: dict) -> str:
    title = row.get("title", "Unknown")
    lesson_date = row.get("lesson_date", "N/A")
    lesson_type = row.get("lesson_type", "N/A")
    summary = redact_secrets(row.get("summary"))
    key_takeaways = fmt(row.get("key_takeaways"))
    related_failure_id = row.get("related_failure_id", "N/A")
    related_decision_id = row.get("related_decision_id", "N/A")
    confidence = row.get("confidence_score", "N/A")
    created = row.get("created_at", "N/A")
    row_id = row.get("id", "N/A")

    q_score = row.get('quality_score', 0)
    q_grade = row.get('quality_grade', 'F')
    q_evidence = row.get('evidence_score', 0)
    q_impact = row.get('impact_score', 0)
    q_reuse = row.get('reuse_score', 0)
    q_conf = row.get('q_confidence_score', 0)
    q_action = row.get('actionability_score', 0)
    q_updated = row.get('quality_last_updated', 'N/A')

    return f"""---
schema: lesson
table: lesson_registry
id: {row_id}
title: {title}
lesson_type: {lesson_type}
created: {created}
quality_score: {q_score}
quality_grade: {q_grade}
---

# 📖 {title}

## Metadata

| Field | Value |
|---|---|
| ID | `{row_id}` |
| Title | {title} |
| Type | {lesson_type} |
| Date | {lesson_date} |
| Confidence | {confidence} |
| Related Failure | `{related_failure_id}` |
| Related Decision | `{related_decision_id}` |
| Created | {created} |

## Summary

{summary}

## Key Takeaways

```json
{key_takeaways}
```

## Quality Score

| Metric | Score |
|---|---|
| Total | **{q_score}** / 100 ({q_grade}) |
| Evidence | {q_evidence} / 20 |
| Impact | {q_impact} / 20 |
| Reuse | {q_reuse} / 20 |
| Confidence | {q_conf} / 20 |
| Actionability | {q_action} / 20 |
| Updated | {q_updated} |

## Source

- Database: `knowledge_os`
- Schema: `lesson`
- Table: `lesson_registry`
- Row: `{row_id}`
"""


def generate_agent_md(row: dict) -> str:
    agent = row.get("agent_name", "Unknown")
    memory_key = row.get("memory_key", "Unknown")
    memory_type = row.get("memory_type", "N/A")
    memory_value = redact_secrets(row.get("memory_value"))
    confidence = row.get("confidence_score", "N/A")
    source = row.get("source", "N/A")
    created = row.get("created_at", "N/A")
    updated = row.get("updated_at", "N/A")
    row_id = row.get("id", "N/A")

    q_score = row.get('quality_score', 0)
    q_grade = row.get('quality_grade', 'F')
    q_evidence = row.get('evidence_score', 0)
    q_impact = row.get('impact_score', 0)
    q_reuse = row.get('reuse_score', 0)
    q_conf = row.get('q_confidence_score', 0)
    q_action = row.get('actionability_score', 0)
    q_updated = row.get('quality_last_updated', 'N/A')

    return f"""---
schema: agent
table: agent_memory_registry
id: {row_id}
agent: {agent}
memory_type: {memory_type}
key: {memory_key}
created: {created}
updated: {updated}
quality_score: {q_score}
quality_grade: {q_grade}
---

# 🤖 {agent} — {memory_key}

## Metadata

| Field | Value |
|---|---|
| ID | `{row_id}` |
| Agent | {agent} |
| Memory Type | {memory_type} |
| Key | `{memory_key}` |
| Confidence | {confidence} |
| Source | {source} |
| Created | {created} |
| Updated | {updated} |

## Value

{memory_value}

## Quality Score

| Metric | Score |
|---|---|
| Total | **{q_score}** / 100 ({q_grade}) |
| Evidence | {q_evidence} / 20 |
| Impact | {q_impact} / 20 |
| Reuse | {q_reuse} / 20 |
| Confidence | {q_conf} / 20 |
| Actionability | {q_action} / 20 |
| Updated | {q_updated} |

## Source

- Database: `knowledge_os`
- Schema: `agent`
- Table: `agent_memory_registry`
- Row: `{row_id}`
"""


GENERATORS = {
    "knowledge": generate_knowledge_md,
    "decision": generate_decision_md,
    "failure": generate_failure_md,
    "lesson": generate_lesson_md,
    "agent": generate_agent_md,
}


# ============================================================
# State Management
# ============================================================

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    state["last_export"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ============================================================
# Export Logic
# ============================================================

def get_connection():
    if not DB_CONFIG["password"]:
        raise ValueError("POSTGRES_PASSWORD not set.")
    return psycopg2.connect(**DB_CONFIG)


def export_schema(conn, schema_name: str, config: dict, mode: str, last_export: str, dry_run: bool) -> dict:
    """Export a single schema's registry table to Markdown files."""
    table = config["table"]
    folder = config["folder"]
    slug_prefix = config["slug_prefix"]
    generator = GENERATORS[schema_name]

    folder_path = os.path.join(VAULT_ROOT, folder)
    os.makedirs(folder_path, exist_ok=True)

    # Check if table has updated_at column
    has_updated = False
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s AND column_name = 'updated_at'
            )
        """, (schema_name, table))
        has_updated = cur.fetchone()[0]

    # Build query — use updated_at if available, else created_at
    timestamp_col = "updated_at" if has_updated else "created_at"
    query = f"SELECT * FROM {schema_name}.{table}"
    if mode == "incremental" and last_export:
        query += f" WHERE {timestamp_col} > '{last_export}'"
    query += " ORDER BY created_at"

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    result = {"schema": schema_name, "table": table, "exported": 0, "files": []}

    for row in rows:
        row_dict = dict(row)
        # Convert datetime objects to ISO strings
        for k, v in row_dict.items():
            if hasattr(v, "isoformat"):
                row_dict[k] = v.isoformat()

        # Generate filename
        title_key = config["title_field"]
        title_val = str(row_dict.get(title_key, row_dict.get("id", "unknown")))
        slug = slugify(title_val)
        filename = f"{slug_prefix}-{slug}.md"
        filepath = os.path.join(folder_path, filename)

        # Generate markdown
        md_content = generator(row_dict)

        if dry_run:
            result["files"].append(filename)
            result["exported"] += 1
            continue

        # Write file (safe overwrite)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        result["files"].append(filename)
        result["exported"] += 1

    return result


def run_export(mode: str = "full", dry_run: bool = False):
    """Main export entry point."""
    print(f"\n{'='*60}")
    print(f"  PostgreSQL → Obsidian Markdown Exporter")
    print(f"  Mode: {'DRY RUN' if dry_run else mode}")
    print(f"  Vault: {VAULT_ROOT}")
    print(f"  Time: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}\n")

    conn = get_connection()
    state = load_state()
    last_export = state.get("last_export", "") if mode == "incremental" else ""
    results = []

    try:
        for schema_name, config in SCHEMA_MAP.items():
            print(f"  Exporting: {schema_name}.{config['table']} → {config['folder']}/")
            result = export_schema(conn, schema_name, config, mode, last_export, dry_run)
            results.append(result)
            print(f"    → {result['exported']} files exported")
            for f in result["files"]:
                print(f"       {f}")

        # Summary
        total = sum(r["exported"] for r in results)
        print(f"\n{'='*60}")
        print(f"  EXPORT SUMMARY")
        print(f"{'='*60}")
        for r in results:
            status = "✅" if r["exported"] > 0 else "⚠️  (no records)"
            print(f"  {status} {r['schema']:12s} → {r['exported']:3d} files → {SCHEMA_MAP[r['schema']]['folder']}/")
        print(f"  {'─'*50}")
        print(f"  Total: {total} files exported")

        if not dry_run:
            save_state(state)
            print(f"  State saved: {STATE_FILE}")

        print(f"\n{'='*60}")
        print(f"  RESULT: {'DRY RUN COMPLETE' if dry_run else 'EXPORT COMPLETE'}")
        print(f"{'='*60}\n")

        return results

    finally:
        conn.close()


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export PostgreSQL Knowledge OS to Obsidian Markdown")
    parser.add_argument("--mode", choices=["full", "incremental"], default="full", help="Export mode")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    args = parser.parse_args()
    run_export(mode=args.mode, dry_run=args.dry_run)
