#!/usr/bin/env python3
"""
CAPTAIN MOD OS — Notion Sync Engine
PostgreSQL (Source of Truth) → Notion (Presentation Layer)

Usage:
    python3 notion_sync.py --all           # Sync all 4 databases
    python3 notion_sync.py --executive     # Executive Dashboard only
    python3 notion_sync.py --knowledge     # Knowledge Assets only
    python3 notion_sync.py --rcaf          # RCAF Registry only
    python3 notion_sync.py --principles    # Organizational Principles only
    python3 notion_sync.py --verify        # Verify sync counts
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

# ── Configuration ──
SECRETS_DIR = '/opt/data/secrets'
NOTION_ENV = os.path.join(SECRETS_DIR, 'notion.env')
PG_CONTAINER = 'knowledge-os-postgres'
PG_USER = 'knowledge_admin'
PG_DB = 'knowledge_os'
NOTION_VERSION = '2022-06-28'

def load_config():
    """Load Notion API key and database IDs from secrets."""
    config = {}
    if not os.path.exists(NOTION_ENV):
        print("ERROR: " + NOTION_ENV + " not found")
        sys.exit(1)

    with open(NOTION_ENV) as f:
        for line in f:
            line = line.strip()
            if '=' in line and line and not line.startswith('#'):
                key, val = line.split('=', 1)
                config[key] = val

    if 'NOTION_API_KEY' not in config:
        print("ERROR: NOTION_API_KEY not in " + NOTION_ENV)
        sys.exit(1)

    return config


def notion_request(method, endpoint, payload=None):
    """Make a Notion API request via curl."""
    config = load_config()
    url = 'https://api.notion.com/v1/' + endpoint
    auth = 'Bearer ' + config['NOTION_API_KEY']

    cmd = ['curl', '-s', '-X', method, url,
           '-H', 'Authorization: ' + auth,
           '-H', 'Notion-Version: ' + NOTION_VERSION,
           '-H', 'Content-Type: application/json']

    if payload:
        cmd.extend(['-d', json.dumps(payload)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)


def pg_query(sql):
    """Execute a PostgreSQL query and return rows as list of dicts."""
    cmd = ['docker', 'exec', PG_CONTAINER,
           'psql', '-U', PG_USER, '-d', PG_DB,
           '-t', '-A', '-F', '|', '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    rows = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            fields = line.split('|')
            rows.append(fields)
    return rows


def pg_query_dicts(sql):
    """Execute PostgreSQL query and return list of dicts."""
    cmd = ['docker', 'exec', PG_CONTAINER,
           'psql', '-U', PG_USER, '-d', PG_DB,
           '-t', '-A', '-F', '|', '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Get column names
    col_cmd = ['docker', 'exec', PG_CONTAINER,
               'psql', '-U', PG_USER, '-d', PG_DB,
               '-t', '-A', '-F', '|', '-c',
               'SELECT 1 FROM ( ' + sql + ' ) sub LIMIT 0']
    # Use header mode to get column names
    hdr_cmd = ['docker', 'exec', PG_CONTAINER,
               'psql', '-U', PG_USER, '-d', PG_DB,
               '-H', '-c', sql]
    hdr_result = subprocess.run(hdr_cmd, capture_output=True, text=True)

    # Parse simple pipe-delimited output
    rows = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            rows.append(line.split('|'))
    return rows


def safe_date(date_str):
    """Convert a date string to ISO format for Notion."""
    if not date_str:
        return None
    try:
        if isinstance(date_str, str):
            # Try common formats
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S%z']:
                try:
                    dt = datetime.strptime(date_str.split('+')[0].split('Z')[0].strip(), fmt.split('%z')[0].strip())
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        return str(date_str)[:10]
    except Exception:
        return None


def safe_number(val):
    """Convert value to a safe number."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def get_existing_pages(database_id):
    """Get all existing pages in a Notion database (for upsert)."""
    pages = {}
    has_more = True
    start_cursor = None

    while has_more:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        result = notion_request('POST', 'databases/' + database_id + '/query', payload)

        for page in result.get('results', []):
            props = page.get('properties', {})
            # Get the title/name for matching
            title_key = None
            for pname, pval in props.items():
                if pval.get('type') == 'title':
                    title_key = pname
                    break

            if title_key:
                title_val = props[title_key].get('title', [])
                title_text = ''.join([t.get('plain_text', '') for t in title_val])
                if title_text:
                    pages[title_text] = page['id']

        has_more = result.get('has_more', False)
        start_cursor = result.get('next_cursor')

    return pages


def upsert_page(database_id, title, properties, existing_pages):
    """Create or update a page in a Notion database."""
    if title in existing_pages:
        # Update existing
        page_id = existing_pages[title]
        payload = {"properties": properties}
        result = notion_request('PATCH', 'pages/' + page_id, payload)
        if 'id' in result:
            return ('updated', page_id)
        else:
            return ('error', result.get('message', 'unknown'))
    else:
        # Create new
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        result = notion_request('POST', 'pages', payload)
        if 'id' in result:
            return ('created', result['id'])
        else:
            return ('error', result.get('message', 'unknown'))


# ═══════════════════════════════════════════════
# SYNC FUNCTIONS
# ═══════════════════════════════════════════════

def sync_executive_dashboard():
    """Sync dashboard metrics to Executive Dashboard database."""
    config = load_config()
    db_id = config.get('NOTION_DB_EXECUTIVE_DASHBOARD')
    if not db_id:
        print("ERROR: NOTION_DB_EXECUTIVE_DASHBOARD not set")
        return False

    print("\n── Syncing Executive Dashboard ──")
    existing = get_existing_pages(db_id)
    print("  Existing Notion pages: " + str(len(existing)))

    # Fetch metrics from PostgreSQL
    rows = pg_query_dicts(
        "SELECT metric_name, metric_value, metric_category "
        "FROM dashboard.dashboard_metrics ORDER BY metric_category, metric_name"
    )

    created = 0
    updated = 0
    errors = 0

    for row in rows:
        metric_name = row[0]
        metric_value = safe_number(row[1])
        metric_category = row[2] if len(row) > 2 else ''

        # Determine category display
        cat_map = {
            'KPI:system': 'System',
            'KPI:knowledge': 'Knowledge',
            'KPI:governance': 'Governance',
            'KPI:automation': 'Automation',
            'count:knowledge': 'Knowledge',
            'count:governance': 'Governance',
            'count:rcaf': 'RCAF',
        }
        category_display = cat_map.get(metric_category, metric_category.split(':')[-1] if ':' in metric_category else metric_category)

        # Determine grade for KPI metrics
        grade = None
        status = 'Active'
        if 'KPI' in metric_category and metric_value is not None:
            if metric_value >= 95:
                grade = 'A+'
            elif metric_value >= 90:
                grade = 'A'
            elif metric_value >= 80:
                grade = 'B'
            elif metric_value >= 70:
                grade = 'C'
            elif metric_value >= 60:
                grade = 'D'
            else:
                grade = 'F'

            if metric_value < 60:
                status = 'Critical'
            elif metric_value < 80:
                status = 'Degraded'

        props = {
            "Metric Name": {"title": [{"text": {"content": metric_name}}]},
            "Metric Category": {"select": {"name": category_display}},
            "Last Updated": {"date": {"start": datetime.utcnow().strftime('%Y-%m-%d')}},
        }

        if metric_value is not None:
            props["Metric Value"] = {"number": metric_value}
        if grade:
            props["Health Grade"] = {"select": {"name": grade}}
        props["Status"] = {"select": {"name": status}}

        action, result = upsert_page(db_id, metric_name, props, existing)
        if action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1
        else:
            errors += 1
            print("  ERROR: " + metric_name + " — " + str(result))

    print("  Created: " + str(created) + " | Updated: " + str(updated) + " | Errors: " + str(errors))
    return errors == 0


def sync_knowledge_assets():
    """Sync curated assets to Knowledge Assets database."""
    config = load_config()
    db_id = config.get('NOTION_DB_KNOWLEDGE_ASSETS')
    if not db_id:
        print("ERROR: NOTION_DB_KNOWLEDGE_ASSETS not set")
        return False

    print("\n── Syncing Knowledge Assets ──")
    existing = get_existing_pages(db_id)
    print("  Existing Notion pages: " + str(len(existing)))

    # Fetch from curated_assets
    rows = pg_query_dicts(
        "SELECT asset_id, asset_name, category, quality_score, status, "
        "created_at, updated_at "
        "FROM knowledge.curated_assets ORDER BY quality_score DESC"
    )

    created = 0
    updated = 0
    errors = 0

    for row in rows:
        asset_name = row[1]
        category = row[2].upper() if row[2] else 'KNOWLEDGE'
        quality_score = safe_number(row[3])
        status = row[4] or 'active'

        # Quality grade
        grade = 'F'
        if quality_score:
            if quality_score >= 95:
                grade = 'A+'
            elif quality_score >= 90:
                grade = 'A'
            elif quality_score >= 80:
                grade = 'B'
            elif quality_score >= 70:
                grade = 'C'
            elif quality_score >= 60:
                grade = 'D'

        # Ensure valid select values
        valid_categories = ['KNOWLEDGE', 'DECISION', 'FAILURE', 'LESSON', 'AGENT_MEMORY']
        if category not in valid_categories:
            category = 'KNOWLEDGE'

        valid_statuses = ['active', 'archived', 'promoted', 'draft']
        if status not in valid_statuses:
            status = 'active'

        props = {
            "Title": {"title": [{"text": {"content": asset_name}}]},
            "Category": {"select": {"name": category}},
            "Status": {"select": {"name": status}},
            "Source Registry": {"select": {"name": "curated_assets"}},
        }

        if quality_score is not None:
            props["Quality Score"] = {"number": quality_score}
        props["Quality Grade"] = {"select": {"name": grade}}

        created_date = safe_date(row[5])
        updated_date = safe_date(row[6])
        if created_date:
            props["Created"] = {"date": {"start": created_date}}
        if updated_date:
            props["Updated"] = {"date": {"start": updated_date}}

        action, result = upsert_page(db_id, asset_name, props, existing)
        if action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1
        else:
            errors += 1
            print("  ERROR: " + asset_name + " — " + str(result))

    print("  Created: " + str(created) + " | Updated: " + str(updated) + " | Errors: " + str(errors))
    return errors == 0


def sync_rcaf_registry():
    """Sync failures, lessons, agent memories to RCAF Registry database."""
    config = load_config()
    db_id = config.get('NOTION_DB_RCAF_REGISTRY')
    if not db_id:
        print("ERROR: NOTION_DB_RCAF_REGISTRY not set")
        return False

    print("\n── Syncing RCAF Registry ──")
    existing = get_existing_pages(db_id)
    print("  Existing Notion pages: " + str(len(existing)))

    created = 0
    updated = 0
    errors = 0

    # ── Failures ──
    fail_rows = pg_query_dicts(
        "SELECT id, system_name, failure_type, severity, symptom, status, "
        "quality_score, created_at "
        "FROM failure.failure_registry ORDER BY quality_score DESC"
    )
    for row in fail_rows:
        name = row[1] + ' — ' + row[2] if row[1] and row[2] else (row[1] or 'Unknown Failure')
        severity = (row[3] or 'MEDIUM').upper()
        status = row[5] or 'open'
        quality_score = safe_number(row[6])

        valid_sev = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        if severity not in valid_sev:
            severity = 'MEDIUM'
        valid_stat = ['active', 'resolved', 'archived', 'open']
        if status not in valid_stat:
            status = 'active'

        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Type": {"select": {"name": "Failure"}},
            "Severity": {"select": {"name": severity}},
            "Status": {"select": {"name": status}},
            "Source Table": {"rich_text": [{"text": {"content": "failure.failure_registry"}}]},
        }
        if quality_score is not None:
            props["Quality Score"] = {"number": quality_score}
        created_date = safe_date(row[7])
        if created_date:
            props["Created"] = {"date": {"start": created_date}}

        action, result = upsert_page(db_id, name, props, existing)
        if action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1
        else:
            errors += 1

    # ── Lessons ──
    lesson_rows = pg_query_dicts(
        "SELECT id, title, lesson_type, quality_score, created_at "
        "FROM lesson.lesson_registry ORDER BY quality_score DESC"
    )
    for row in lesson_rows:
        name = row[1] or 'Unnamed Lesson'
        quality_score = safe_number(row[3])

        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Type": {"select": {"name": "Lesson"}},
            "Severity": {"select": {"name": "MEDIUM"}},
            "Status": {"select": {"name": "active"}},
            "Source Table": {"rich_text": [{"text": {"content": "lesson.lesson_registry"}}]},
        }
        if quality_score is not None:
            props["Quality Score"] = {"number": quality_score}
        created_date = safe_date(row[4])
        if created_date:
            props["Created"] = {"date": {"start": created_date}}

        action, result = upsert_page(db_id, name, props, existing)
        if action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1
        else:
            errors += 1

    # ── Agent Memories (top 20 by quality) ──
    agent_rows = pg_query_dicts(
        "SELECT id, memory_key, memory_type, quality_score, created_at "
        "FROM agent.agent_memory_registry "
        "WHERE memory_type = 'preventive_rule' "
        "ORDER BY quality_score DESC LIMIT 20"
    )
    for row in agent_rows:
        name = row[1] or 'Unnamed Rule'
        quality_score = safe_number(row[3])

        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Type": {"select": {"name": "Rule"}},
            "Severity": {"select": {"name": "LOW"}},
            "Status": {"select": {"name": "active"}},
            "Source Table": {"rich_text": [{"text": {"content": "agent.agent_memory_registry"}}]},
        }
        if quality_score is not None:
            props["Quality Score"] = {"number": quality_score}
        created_date = safe_date(row[4])
        if created_date:
            props["Created"] = {"date": {"start": created_date}}

        action, result = upsert_page(db_id, name, props, existing)
        if action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1
        else:
            errors += 1

    print("  Created: " + str(created) + " | Updated: " + str(updated) + " | Errors: " + str(errors))
    return errors == 0


def sync_principles():
    """Sync governance records to Organizational Principles database."""
    config = load_config()
    db_id = config.get('NOTION_DB_ORGANIZATIONAL_PRINCIPLES')
    if not db_id:
        print("ERROR: NOTION_DB_ORGANIZATIONAL_PRINCIPLES not set")
        return False

    print("\n── Syncing Organizational Principles ──")
    existing = get_existing_pages(db_id)
    print("  Existing Notion pages: " + str(len(existing)))

    created = 0
    updated = 0
    errors = 0

    # ── Principles ──
    rows = pg_query_dicts(
        "SELECT principle_id, principle_name, principle_statement, "
        "quality_score, status, created_at "
        "FROM governance.organizational_principles ORDER BY quality_score DESC"
    )
    for row in rows:
        name = row[1] or 'Unnamed Principle'
        statement = row[2] or ''
        quality_score = safe_number(row[3])
        status = row[4] or 'active'

        valid_stat = ['active', 'draft', 'archived']
        if status not in valid_stat:
            status = 'active'

        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Type": {"select": {"name": "Principle"}},
            "Status": {"select": {"name": status}},
            "Description": {"rich_text": [{"text": {"content": statement[:2000]}}]},
        }
        if quality_score is not None:
            props["Quality Score"] = {"number": quality_score}
            props["Compliance"] = {"number": quality_score / 100.0}
        created_date = safe_date(row[5])
        if created_date:
            props["Created"] = {"date": {"start": created_date}}

        action, result = upsert_page(db_id, name, props, existing)
        if action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1
        else:
            errors += 1

    # ── Policies ──
    pol_rows = pg_query_dicts(
        "SELECT policy_id, policy_name, policy_statement, status, created_at "
        "FROM governance.policy_registry ORDER BY created_at DESC"
    )
    for row in pol_rows:
        name = row[1] or 'Unnamed Policy'
        statement = row[2] or ''
        status = row[3] or 'active'

        valid_stat = ['active', 'draft', 'archived']
        if status not in valid_stat:
            status = 'active'

        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Type": {"select": {"name": "Policy"}},
            "Status": {"select": {"name": status}},
            "Description": {"rich_text": [{"text": {"content": statement[:2000]}}]},
        }
        created_date = safe_date(row[4])
        if created_date:
            props["Created"] = {"date": {"start": created_date}}

        action, result = upsert_page(db_id, name, props, existing)
        if action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1
        else:
            errors += 1

    # ── Rules ──
    rule_rows = pg_query_dicts(
        "SELECT rule_id, rule_name, rule_statement, status, created_at "
        "FROM governance.rule_registry ORDER BY created_at DESC"
    )
    for row in rule_rows:
        name = row[1] or 'Unnamed Rule'
        statement = row[2] or ''
        status = row[3] or 'active'

        valid_stat = ['active', 'draft', 'archived']
        if status not in valid_stat:
            status = 'active'

        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Type": {"select": {"name": "Rule"}},
            "Status": {"select": {"name": status}},
            "Description": {"rich_text": [{"text": {"content": statement[:2000]}}]},
        }
        created_date = safe_date(row[4])
        if created_date:
            props["Created"] = {"date": {"start": created_date}}

        action, result = upsert_page(db_id, name, props, existing)
        if action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1
        else:
            errors += 1

    # ── SOPs ──
    sop_rows = pg_query_dicts(
        "SELECT sop_id, sop_name, objective, status, created_at "
        "FROM governance.sop_library ORDER BY created_at DESC"
    )
    for row in sop_rows:
        name = row[1] or 'Unnamed SOP'
        objective = row[2] or ''
        status = row[3] or 'active'

        valid_stat = ['active', 'draft', 'archived']
        if status not in valid_stat:
            status = 'active'

        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Type": {"select": {"name": "SOP"}},
            "Status": {"select": {"name": status}},
            "Description": {"rich_text": [{"text": {"content": objective[:2000]}}]},
        }
        created_date = safe_date(row[4])
        if created_date:
            props["Created"] = {"date": {"start": created_date}}

        action, result = upsert_page(db_id, name, props, existing)
        if action == 'created':
            created += 1
        elif action == 'updated':
            updated += 1
        else:
            errors += 1

    print("  Created: " + str(created) + " | Updated: " + str(updated) + " | Errors: " + str(errors))
    return errors == 0


def verify_sync():
    """Verify record counts match between PostgreSQL and Notion."""
    config = load_config()
    print("\n── Verifying Sync ──")

    checks = [
        ("Executive Dashboard", "NOTION_DB_EXECUTIVE_DASHBOARD", "SELECT count(*) FROM dashboard.dashboard_metrics"),
        ("Knowledge Assets", "NOTION_DB_KNOWLEDGE_ASSETS", "SELECT count(*) FROM knowledge.curated_assets"),
        ("RCAF Registry", "NOTION_DB_RCAF_REGISTRY",
         "SELECT count(*) FROM failure.failure_registry "
         "UNION ALL SELECT count(*) FROM lesson.lesson_registry "
         "UNION ALL SELECT (SELECT count(*) FROM agent.agent_memory_registry WHERE memory_type = 'preventive_rule') "
         "UNION ALL SELECT 0"),
        ("Organizational Principles", "NOTION_DB_ORGANIZATIONAL_PRINCIPLES",
         "SELECT count(*) FROM governance.organizational_principles "
         "UNION ALL SELECT count(*) FROM governance.policy_registry "
         "UNION ALL SELECT count(*) FROM governance.rule_registry "
         "UNION ALL SELECT count(*) FROM governance.sop_library "
         "UNION ALL SELECT 0"),
    ]

    all_pass = True
    for name, db_key, sql in checks:
        db_id = config.get(db_key)
        if not db_id:
            print("  " + name + ": SKIP (no DB ID)")
            continue

        # Count in Notion
        result = notion_request('POST', 'databases/' + db_id + '/query', {"page_size": 100})
        notion_count = len(result.get('results', []))

        # Count in PostgreSQL
        pg_rows = pg_query_dicts(sql)
        pg_total = sum(int(r[0]) for r in pg_rows if r[0].isdigit())

        match = "MATCH" if notion_count == pg_total else "MISMATCH"
        if match == "MISMATCH":
            all_pass = False
        print("  " + name + ": Notion=" + str(notion_count) + " PostgreSQL=" + str(pg_total) + " " + match)

    return all_pass


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Notion Sync Engine')
    parser.add_argument('--all', action='store_true', help='Sync all databases')
    parser.add_argument('--executive', action='store_true', help='Sync Executive Dashboard')
    parser.add_argument('--knowledge', action='store_true', help='Sync Knowledge Assets')
    parser.add_argument('--rcaf', action='store_true', help='Sync RCAF Registry')
    parser.add_argument('--principles', action='store_true', help='Sync Organizational Principles')
    parser.add_argument('--verify', action='store_true', help='Verify sync counts')
    args = parser.parse_args()

    if not any([args.all, args.executive, args.knowledge, args.rcaf, args.principles, args.verify]):
        parser.print_help()
        sys.exit(1)

    start = datetime.utcnow()
    print("=" * 60)
    print("NOTION SYNC ENGINE — " + start.strftime('%Y-%m-%d %H:%M:%S UTC'))
    print("=" * 60)

    results = {}

    if args.all or args.executive:
        results['executive'] = sync_executive_dashboard()
    if args.all or args.knowledge:
        results['knowledge'] = sync_knowledge_assets()
    if args.all or args.rcaf:
        results['rcaf'] = sync_rcaf_registry()
    if args.all or args.principles:
        results['principles'] = sync_principles()
    if args.verify:
        results['verify'] = verify_sync()

    elapsed = (datetime.utcnow() - start).total_seconds()

    print("\n" + "=" * 60)
    print("SYNC COMPLETE — " + str(round(elapsed, 1)) + "s")
    print("=" * 60)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print("  " + name + ": " + status)

    all_pass = all(results.values())
    print("\nOVERALL: " + ("PASS" if all_pass else "FAIL"))
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
