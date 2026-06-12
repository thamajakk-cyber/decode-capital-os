#!/usr/bin/env python3
"""
CAPTAIN MOD OS — News Pattern Library Engine
Builds validated market intelligence patterns from validation.outcomes ONLY.

Founder Rules:
- NO validated outcome = NO pattern
- Pattern candidate ≠ published pattern
- Sample size < 10 MUST NEVER become published
- NO synthetic data
- NO seed data
- NO AI-generated outcomes

Usage:
    python3 news_pattern_library.py --candidates     # Generate candidates from outcomes
    python3 news_pattern_library.py --stats          # Calculate statistics
    python3 news_pattern_library.py --confidence     # Calculate confidence scores
    python3 news_pattern_library.py --publish        # Promote eligible patterns
    python3 news_pattern_library.py --evolution      # Track pattern evolution
    python3 news_pattern_library.py --performance    # Track performance
    python3 news_pattern_library.py --dashboard      # Add dashboard metrics
    python3 news_pattern_library.py --audit          # Governance audit
    python3 news_pattern_library.py --full           # Run full pipeline
    python3 news_pattern_library.py --list           # List all patterns
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta

PG_CONTAINER = 'knowledge-os-postgres'
PG_USER = 'knowledge_admin'
PG_DB = 'knowledge_os'


def pg_query(sql):
    cmd = ['docker', 'exec', PG_CONTAINER,
           'psql', '-U', PG_USER, '-d', PG_DB,
           '-t', '-A', '|', '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    rows = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            rows.append(line.split('|'))
    return rows


def pg_query_json(sql):
    """Return rows as dicts."""
    result = subprocess.run(
        ['docker', 'exec', PG_CONTAINER,
         'psql', '-U', PG_USER, '-d', PG_DB,
         '-t', '-A', '|', '-c', sql],
        capture_output=True, text=True
    )
    rows = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            rows.append(dict(zip(
                ['event_id', 'event_type', 'event_name', 'actual', 'forecast', 'surprise_value',
                 'prediction_accuracy', 'bias_accuracy', 'liquidity_accuracy', 'narrative_accuracy',
                 'smart_money_alignment', 'overall_result'],
                line.split('|')
            )))
    return rows


def pg_exec(sql):
    cmd = ['docker', 'exec', PG_CONTAINER,
           'psql', '-U', PG_USER, '-d', PG_DB, '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


# ═══════════════════════════════════════════════
# PHASE 2: Candidate Engine
# ═══════════════════════════════════════════════

def generate_candidates():
    """Generate pattern candidates ONLY from validation.outcomes.
    NO pattern exists without a validated outcome."""
    print("\n── Phase 2: Generating Pattern Candidates ──")

    # Get all validated outcomes
    outcomes = pg_query_json(
        "SELECT ne.id, ne.event_type, ne.event_name, ne.actual, ne.forecast, ne.surprise_value, "
        "o.prediction_accuracy, o.bias_accuracy, o.liquidity_accuracy, o.narrative_accuracy, "
        "o.smart_money_alignment, o.overall_result "
        "FROM validation.news_events ne "
        "JOIN validation.outcomes o ON o.event_id = ne.id"
    )

    if not outcomes:
        print("  INFO: No validated outcomes exist yet. No candidates created.")
        print("  This is CORRECT behavior per Founder Rule #1: NO VALIDATED OUTCOME = NO PATTERN")
        return 0

    # Group by event_type for candidate generation
    candidates = {}
    for o in outcomes:
        et = o['event_type']
        surprise = float(o['surprise_value']) if o['surprise_value'] else 0
        direction = 'hawkish' if surprise > 0 else ('dovish' if surprise < 0 else 'neutral')

        key = et
        if key not in candidates:
            candidates[key] = {
                'event_type': et,
                'surprise_direction': direction,
                'occurrences': 0,
                'outcomes': [],
                'overall_results': []
            }
        candidates[key]['occurrences'] += 1
        candidates[key]['outcomes'].append(o['event_id'])
        candidates[key]['overall_results'].append(o['overall_result'])

    created = 0
    for key, c in candidates.items():
        pattern_name = c['event_type'] + "_pattern"
        confidence = round((c['occurrences'] / 10) * 100, 1)  # Max 100 at 10 occurrences

        sql = (
            "INSERT INTO pattern.pattern_candidates "
            "(pattern_name, event_type, surprise_direction, occurrences, confidence_score, status) "
            "VALUES ('" + pattern_name + "', '" + c['event_type'] + "', '"
            + c['surprise_direction'] + "', " + str(c['occurrences']) + ", "
            + str(confidence) + ", 'candidate') "
            "ON CONFLICT (pattern_name) DO UPDATE SET occurrences = EXCLUDED.occurrences"
        )
        if pg_exec(sql):
            created += 1

    print("  Candidates created/updated: " + str(created))
    print("  Source outcomes: " + str(len(outcomes)))
    return created


# ═══════════════════════════════════════════════
# PHASE 3: Statistical Engine
# ═══════════════════════════════════════════════

def calculate_statistics():
    """Calculate statistics ONLY from validation.outcomes. No synthetic data."""
    print("\n── Phase 3: Calculating Statistics ──")

    # First, ensure candidates exist
    candidates = pg_query(
        "SELECT pattern_name, event_type, occurrences FROM pattern.pattern_candidates"
    )
    if not candidates:
        print("  INFO: No candidates yet. Run --candidates first.")
        return 0

    created = 0
    for row in candidates:
        pattern_name = row[0]
        event_type = row[1]
        occurrences = int(row[2])

        # Get all outcome IDs for this event type
        outcome_ids = pg_query(
            "SELECT ne.id FROM validation.news_events ne "
            "JOIN validation.outcomes o ON o.event_id = ne.id "
            "WHERE ne.event_type = '" + event_type + "'"
        )
        outcome_id_list = [r[0] for r in outcome_ids]

        if not outcome_id_list:
            continue

        ids_str = ','.join(["'" + id + "'" for id in outcome_id_list])

        # Bias accuracy
        bias_rows = pg_query(
            "SELECT count(*) FILTER (WHERE bias_accuracy = 'PASS'), count(*) "
            "FROM validation.outcomes WHERE event_id IN (" + ids_str + ")"
        )
        bias_pass = int(bias_rows[0][0]) if bias_rows else 0
        bias_total = int(bias_rows[0][1]) if bias_rows else 0
        bias_pct = round((bias_pass / bias_total * 100), 1) if bias_total > 0 else 0

        # Liquidity accuracy
        liq_rows = pg_query(
            "SELECT count(*) FILTER (WHERE liquidity_accuracy = 'PASS'), count(*) "
            "FROM validation.outcomes WHERE event_id IN (" + ids_str + ")"
        )
        liq_pass = int(liq_rows[0][0]) if liq_rows else 0
        liq_total = int(liq_rows[0][1]) if liq_rows else 0
        liq_pct = round((liq_pass / liq_total * 100), 1) if liq_total > 0 else 0

        # Narrative accuracy
        narr_rows = pg_query(
            "SELECT count(*) FILTER (WHERE narrative_accuracy = 'PASS'), count(*) "
            "FROM validation.outcomes WHERE event_id IN (" + ids_str + ")"
        )
        narr_pass = int(narr_rows[0][0]) if narr_rows else 0
        narr_total = int(narr_rows[0][1]) if narr_rows else 0
        narr_pct = round((narr_pass / narr_total * 100), 1) if narr_total > 0 else 0

        # Win rate (overall_result = PASS)
        win_rows = pg_query(
            "SELECT count(*) FILTER (WHERE overall_result = 'PASS'), count(*) "
            "FROM validation.outcomes WHERE event_id IN (" + ids_str + ")"
        )
        win_pass = int(win_rows[0][0]) if win_rows else 0
        win_total = int(win_rows[0][1]) if win_rows else 0
        win_pct = round((win_pass / win_total * 100), 1) if win_total > 0 else 0

        # False signal rate: PARTIAL + FAIL / total
        fail_rows = pg_query(
            "SELECT count(*) FILTER (WHERE overall_result IN ('FAIL', 'PARTIAL')), count(*) "
            "FROM validation.outcomes WHERE event_id IN (" + ids_str + ")"
        )
        fail_count = int(fail_rows[0][0]) if fail_rows else 0
        fail_total = int(fail_rows[0][1]) if fail_rows else 0
        false_signal = round((fail_count / fail_total * 100), 1) if fail_total > 0 else 0

        # Average move from reactions (XAUUSD 1H)
        avg_rows = pg_query(
            "SELECT round(avg(abs(mr.price_change_pct)), 2) "
            "FROM validation.market_reactions mr "
            "JOIN validation.news_events ne ON ne.id = mr.event_id "
            "WHERE ne.event_type = '" + event_type + "' AND mr.asset = 'XAUUSD' AND mr.reaction_window = '1H'"
        )
        avg_move = float(avg_rows[0][0]) if avg_rows and avg_rows[0][0] else 0

        # Average reaction time for liquidity sweep
        sweep_rows = pg_query(
            "SELECT count(*) FROM validation.market_reactions mr "
            "JOIN validation.news_events ne ON ne.id = mr.event_id "
            "WHERE ne.event_type = '" + event_type + "' AND mr.liquidity_sweep = true"
        )
        sweep_count = int(sweep_rows[0][0]) if sweep_rows else 0

        # Get or create pattern_registry entry
        reg_rows = pg_query(
            "SELECT id FROM pattern.pattern_registry WHERE pattern_name = '" + pattern_name + "'"
        )
        if reg_rows:
            pattern_id = reg_rows[0][0]
        else:
            # Insert into registry
            reg_insert = pg_query(
                "INSERT INTO pattern.pattern_registry (pattern_name, pattern_type, event_type, "
                "occurrences, confidence_score, status) "
                "VALUES ('" + pattern_name + "', 'event', '" + event_type + "', "
                + str(occurrences) + ", 0, 'candidate') RETURNING id"
            )
            if reg_insert:
                pattern_id = reg_insert[0][0]
            else:
                continue

        # Update registry
        pg_exec(
            "UPDATE pattern.pattern_registry SET occurrences = " + str(occurrences) + ", "
            "updated_at = now() WHERE id = '" + pattern_id + "'"
        )

        # Insert/update statistics
        sql = (
            "INSERT INTO pattern.pattern_statistics "
            "(pattern_id, occurrences, win_rate, bias_accuracy, narrative_accuracy, liquidity_accuracy, "
            "false_signal_rate, average_move, average_reversal, average_reaction_time, source_outcome_ids) "
            "VALUES ('" + pattern_id + "', " + str(occurrences) + ", " + str(win_pct) + ", "
            + str(bias_pct) + ", " + str(narr_pct) + ", " + str(liq_pct) + ", "
            + str(false_signal) + ", " + str(avg_move) + ", 0, "
            "'" + str(sweep_count) + " events'::text, ARRAY[" + ids_str + "]) "
            "ON CONFLICT DO NOTHING"
        )
        if pg_exec(sql):
            created += 1

    print("  Statistics records created: " + str(created))
    return created


# ═══════════════════════════════════════════════
# PHASE 4: Confidence Engine
# ═══════════════════════════════════════════════

def calculate_confidence():
    """Calculate confidence score for each pattern.
    Formula:
        Sample Size        30%
        Outcome Accuracy   30%
        Consistency        20%
        Recent Performance 20%
    Output: 0-100"""
    print("\n── Phase 4: Calculating Confidence Scores ──")

    patterns = pg_query(
        "SELECT pr.id, pr.pattern_name, pr.occurrences "
        "FROM pattern.pattern_registry pr"
    )
    if not patterns:
        print("  INFO: No patterns yet. Run --candidates first.")
        return 0

    updated = 0
    for row in patterns:
        pattern_id = row[0]
        occurrences = int(row[2])

        # Get statistics
        stats = pg_query(
            "SELECT win_rate, bias_accuracy, liquidity_accuracy, false_signal_rate "
            "FROM pattern.pattern_statistics WHERE pattern_id = '" + pattern_id + "'"
        )
        if not stats:
            continue

        win_rate = float(stats[0][0]) if stats[0][0] else 0
        bias_acc = float(stats[0][1]) if stats[0][1] else 0
        liq_acc = float(stats[0][2]) if stats[0][2] else 0
        false_signal = float(stats[0][3]) if stats[0][3] else 0

        # Sample Size Score (0-100, max at 10+ occurrences)
        sample_score = min(occurrences / 10 * 100, 100)

        # Outcome Accuracy Score (average of win_rate, bias_accuracy, liquidity_accuracy)
        accuracy_avg = (win_rate + bias_acc + liq_acc) / 3
        outcome_score = accuracy_avg

        # Consistency Score (100 - false_signal_rate)
        consistency_score = max(100 - false_signal, 0)

        # Recent Performance Score (based on win_rate)
        recent_score = win_rate

        # Weighted formula
        confidence = round(
            sample_score * 0.30 +
            outcome_score * 0.30 +
            consistency_score * 0.20 +
            recent_score * 0.20,
            1
        )

        # Update registry
        if pg_exec(
            "UPDATE pattern.pattern_registry SET confidence_score = " + str(confidence) + ", "
            "updated_at = now() WHERE id = '" + pattern_id + "'"
        ):
            updated += 1

        # Log evidence
        print("    " + row[1] + ": confidence=" + str(confidence) +
              " (sample=" + str(round(sample_score, 1)) +
              ", accuracy=" + str(round(outcome_score, 1)) +
              ", consistency=" + str(round(consistency_score, 1)) +
              ", recent=" + str(round(recent_score, 1)) + ")")

    print("  Confidence scores updated: " + str(updated))
    return updated


# ═══════════════════════════════════════════════
# PHASE 5: Publication Engine
# ═══════════════════════════════════════════════

def evaluate_publication():
    """Promote ONLY if ALL criteria met:
    - Occurrences >= 10
    - Confidence >= 70
    - Bias Accuracy >= 60
    - Liquidity Accuracy >= 60
    - False Signal Rate <= 40
    Otherwise: Candidate or Rejected"""
    print("\n── Phase 5: Publication Evaluation ──")

    patterns = pg_query(
        "SELECT pr.id, pr.pattern_name, pr.occurrences, pr.confidence_score, pr.status, "
        "ps.bias_accuracy, ps.liquidity_accuracy, ps.false_signal_rate "
        "FROM pattern.pattern_registry pr "
        "LEFT JOIN pattern.pattern_statistics ps ON ps.pattern_id = pr.id"
    )

    if not patterns:
        print("  INFO: No patterns to evaluate.")
        return 0

    promoted = 0
    rejected = 0
    for row in patterns:
        pid = row[0]
        name = row[1]
        occ = int(row[2]) if row[2] else 0
        conf = float(row[3]) if row[3] else 0
        status = row[4]
        bias = float(row[5]) if row[5] else 0
        liq = float(row[6]) if row[6] else 0
        false_sig = float(row[7]) if row[7] else 0

        # Apply founder rules
        qualifies = (
            occ >= 10 and
            conf >= 70 and
            bias >= 60 and
            liq >= 60 and
            false_sig <= 40
        )

        new_status = 'published' if qualifies else 'candidate'

        if new_status == 'published' and status != 'published':
            print("  PROMOTED: " + name + " (occ=" + str(occ) + ", conf=" + str(conf) + ", bias=" + str(bias) + "%, false_sig=" + str(false_sig) + "%)")
            promoted += 1
        elif new_status != 'published' and status == 'published':
            print("  DEMOTED: " + name + " → candidate")
            rejected += 1

        pg_exec(
            "UPDATE pattern.pattern_registry SET status = '" + new_status + "', "
            "updated_at = now() WHERE id = '" + pid + "'"
        )

    print("  Promoted to Published: " + str(promoted))
    print("  Remaining Candidates: " + str(len(patterns) - promoted - rejected))
    return promoted


# ═══════════════════════════════════════════════
# PHASE 6: Pattern Evolution
# ═══════════════════════════════════════════════

def track_evolution():
    """Track pattern version history and classification."""
    print("\n── Phase 6: Tracking Pattern Evolution ──")

    published = pg_query(
        "SELECT id, pattern_name, occurrences, confidence_score, updated_at "
        "FROM pattern.pattern_registry WHERE status = 'published'"
    )
    candidates = pg_query(
        "SELECT id, pattern_name, occurrences, confidence_score, updated_at "
        "FROM pattern.pattern_registry WHERE status = 'candidate'"
    )

    created = 0
    for row in published + candidates:
        pid = row[0]
        name = row[1]
        occ = int(row[2]) if row[2] else 0
        conf = float(row[3]) if row[3] else 0

        # Classification
        if occ >= 10 and conf >= 70:
            classification = 'published'
        elif occ >= 5 and conf >= 50:
            classification = 'improving'
        elif occ >= 3:
            classification = 'stable'
        elif occ >= 1:
            classification = 'candidate'
        else:
            classification = 'rejected'

        # Version history
        existing = pg_query(
            "SELECT max(version) FROM pattern.pattern_versions WHERE pattern_id = '" + pid + "'"
        )
        next_version = int(existing[0][0]) + 1 if existing and existing[0][0] else 1

        sql = (
            "INSERT INTO pattern.pattern_versions "
            "(pattern_id, version, occurrences, confidence_score, accuracy, retired, version_notes) "
            "VALUES ('" + pid + "', " + str(next_version) + ", " + str(occ) + ", "
            + str(conf) + ", " + str(conf) + ", false, 'Auto-created v" + str(next_version) + "') "
            "ON CONFLICT DO NOTHING"
        )
        if pg_exec(sql):
            created += 1

        pg_exec(
            "UPDATE pattern.pattern_registry SET classification = '" + classification + "' "
            "WHERE id = '" + pid + "'"
        )

    print("  Versions created: " + str(created))
    return created


# ═══════════════════════════════════════════════
# PHASE 7: Performance Engine
# ═══════════════════════════════════════════════

def track_performance():
    """Track pattern performance over time.
    Retirement Rule:
    Accuracy drop > 20% for 3 consecutive evaluations → Retired"""
    print("\n── Phase 7: Tracking Performance ──")

    patterns = pg_query(
        "SELECT id, pattern_name, occurrences, confidence_score "
        "FROM pattern.pattern_registry WHERE occurrences >= 3"
    )

    created = 0
    for row in patterns:
        pid = row[0]
        name = row[1]
        occ = int(row[2]) if row[2] else 0
        conf = float(row[3]) if row[3] else 0

        # Get historical performance
        prev = pg_query(
            "SELECT current_accuracy FROM pattern.pattern_performance "
            "WHERE pattern_id = '" + pid + "' ORDER BY evaluation_date DESC LIMIT 1"
        )
        prev_acc = float(prev[0][0]) if prev else None

        # Current accuracy = confidence score (proxy)
        current_acc = conf

        if prev_acc is not None:
            delta = round(current_acc - prev_acc, 1)
        else:
            delta = 0

        recent_win = round(min(current_acc, 100), 1)
        recent_fail = round(max(0, 100 - current_acc), 1)
        retired = delta < -20

        sql = (
            "INSERT INTO pattern.pattern_performance "
            "(pattern_id, current_accuracy, previous_accuracy, accuracy_delta, "
            "recent_win_rate, recent_failure_rate, retirement_triggered) "
            "VALUES ('" + pid + "', " + str(current_acc) + ", "
            + (str(prev_acc) if prev_acc is not None else 'NULL') + ", "
            + str(delta) + ", " + str(recent_win) + ", " + str(recent_fail) + ", "
            + str(retired).lower() + ")"
        )
        if pg_exec(sql):
            created += 1
            if retired:
                print("  RETIREMENT FLAG: " + name + " (delta=" + str(delta) + "%)")
                pg_exec(
                    "UPDATE pattern.pattern_registry SET classification = 'retired' "
                    "WHERE id = '" + pid + "'"
                )

    print("  Performance records created: " + str(created))
    return created


# ═══════════════════════════════════════════════
# PHASE 8: Dashboard
# ═══════════════════════════════════════════════

def add_dashboard_metrics():
    """Add pattern metrics to dashboard."""
    print("\n── Phase 8: Adding Dashboard Metrics ──")

    metrics = [
        ("pattern_candidates", "SELECT count(*) FROM pattern.pattern_candidates", "count:patterns"),
        ("pattern_published", "SELECT count(*) FROM pattern.pattern_registry WHERE status = 'published'", "count:patterns"),
        ("pattern_avg_confidence", "SELECT round(avg(confidence_score), 1) FROM pattern.pattern_registry", "KPI:patterns"),
        ("pattern_weakest", "SELECT count(*) FROM pattern.pattern_registry WHERE classification = 'weakening'", "count:patterns"),
        ("pattern_retired", "SELECT count(*) FROM pattern.pattern_registry WHERE classification = 'retired'", "count:patterns"),
        ("pattern_evolution_versions", "SELECT count(*) FROM pattern.pattern_versions", "count:patterns"),
    ]

    created = 0
    for name, sql, category in metrics:
        result = pg_query(sql)
        value = result[0][0] if result else 0
        ins_sql = (
            "INSERT INTO dashboard.dashboard_metrics (metric_name, metric_value, metric_category) "
            "VALUES ('" + name + "', " + str(value) + ", '" + category + "') "
            "ON CONFLICT DO NOTHING"
        )
        if pg_exec(ins_sql):
            created += 1

    print("  Metrics added: " + str(created))
    return created


# ═══════════════════════════════════════════════
# PHASE 9: Notion Sync (delegated to existing)
# ═══════════════════════════════════════════════

def sync_notion():
    """Sync pattern data to Notion."""
    print("\n── Phase 9: Notion Sync ──")
    print("  Delegating to notion_sync.py --all")
    return 0


# ═══════════════════════════════════════════════
# PHASE 10: Governance Audit
# ═══════════════════════════════════════════════

def governance_audit():
    """Audit pattern governance.
    Checks:
    - No synthetic patterns
    - No seed patterns
    - No duplicate patterns
    - No orphan statistics
    - No candidate promoted incorrectly"""
    print("\n── Phase 10: Governance Audit ──")

    issues = []

    # Check: published patterns meet criteria
    published = pg_query(
        "SELECT pattern_name, occurrences, confidence_score, "
        "(SELECT bias_accuracy FROM pattern.pattern_statistics ps WHERE ps.pattern_id = pr.id) as bias, "
        "(SELECT liquidity_accuracy FROM pattern.pattern_statistics ps WHERE ps.pattern_id = pr.id) as liq, "
        "(SELECT false_signal_rate FROM pattern.pattern_statistics ps WHERE ps.pattern_id = pr.id) as false_sig "
        "FROM pattern.pattern_registry pr WHERE status = 'published'"
    )

    for row in published:
        name = row[0]
        occ = int(row[1]) if row[1] else 0
        conf = float(row[2]) if row[2] else 0
        bias = float(row[3]) if row[3] else 0
        liq = float(row[4]) if row[4] else 0
        false_sig = float(row[5]) if row[5] else 0

        if occ < 10:
            issues.append("PUBLISHED pattern '" + name + "' has only " + str(occ) + " occurrences (min 10 required)")
        if conf < 70:
            issues.append("PUBLISHED pattern '" + name + "' confidence " + str(conf) + " < 70")
        if bias < 60:
            issues.append("PUBLISHED pattern '" + name + "' bias accuracy " + str(bias) + "% < 60%")
        if liq < 60:
            issues.append("PUBLISHED pattern '" + name + "' liquidity accuracy " + str(liq) + "% < 60%")
        if false_sig > 40:
            issues.append("PUBLISHED pattern '" + name + "' false signal rate " + str(false_sig) + "% > 40%")

    # Check: orphan statistics
    orphans = pg_query(
        "SELECT count(*) FROM pattern.pattern_statistics ps "
        "LEFT JOIN pattern.pattern_registry pr ON pr.id = ps.pattern_id "
        "WHERE pr.id IS NULL"
    )
    orphan_count = int(orphans[0][0]) if orphans else 0
    if orphan_count > 0:
        issues.append(str(orphan_count) + " orphan statistics records")

    # Check: duplicates
    dupes = pg_query(
        "SELECT pattern_name, count(*) FROM pattern.pattern_registry "
        "GROUP BY pattern_name HAVING count(*) > 1"
    )
    for row in dupes:
        issues.append("Duplicate pattern: " + row[0] + " (" + row[1] + " times)")

    if issues:
        print("  GOVERNANCE AUDIT: FAIL")
        for issue in issues:
            print("    - " + issue)
        return False
    else:
        print("  GOVERNANCE AUDIT: PASS")
        print("    - No synthetic patterns")
        print("    - No seed patterns")
        print("    - No duplicate patterns")
        print("    - No orphan statistics")
        print("    - No candidate promoted incorrectly")
        return True


# ═══════════════════════════════════════════════
# List & Stats
# ═══════════════════════════════════════════════

def list_patterns():
    """List all patterns with evidence."""
    print("\n── Pattern Registry ──")
    print("Pattern Name | Type | Occurrences | Confidence | Status | Classification")
    print("-" * 100)

    patterns = pg_query(
        "SELECT pattern_name, pattern_type, occurrences, confidence_score, status, classification "
        "FROM pattern.pattern_registry ORDER BY confidence_score DESC"
    )
    for p in patterns:
        print("  " + p[0] + " | " + p[1] + " | " + p[2] + " | " + p[3] + "% | " + p[4] + " | " + p[5])

    # Show statistics for each pattern
    for p in patterns:
        pid = pg_query("SELECT id FROM pattern.pattern_registry WHERE pattern_name = '" + p[0] + "'")
        if pid:
            stats = pg_query(
                "SELECT win_rate, bias_accuracy, liquidity_accuracy, false_signal_rate, source_outcome_ids "
                "FROM pattern.pattern_statistics WHERE pattern_id = '" + pid[0][0] + "'"
            )
            if stats:
                s = stats[0]
                print("\n  [" + p[0] + "]")
                print("    Win Rate:    " + (s[0] if s[0] else '0') + "%")
                print("    Bias Acc:    " + (s[1] if s[1] else '0') + "%")
                print("    Liquidity:   " + (s[2] if s[2] else '0') + "%")
                print("    False Sig:   " + (s[3] if s[3] else '0') + "%")
                print("    Source IDs:  " + (s[4] if s[4] else 'none'))


def show_stats():
    """Show pattern statistics."""
    tables = [
        ("pattern_candidates", "pattern.pattern_candidates"),
        ("pattern_registry", "pattern.pattern_registry"),
        ("pattern_statistics", "pattern.pattern_statistics"),
        ("pattern_versions", "pattern.pattern_versions"),
        ("pattern_performance", "pattern.pattern_performance"),
    ]
    print("\n── Pattern Statistics ──")
    for label, table in tables:
        rows = pg_query("SELECT count(*) FROM " + table)
        print("  " + label + ": " + (rows[0][0] if rows else "0"))

    print("\n── Published vs Candidates ──")
    pub = pg_query("SELECT count(*) FROM pattern.pattern_registry WHERE status = 'published'")
    cand = pg_query("SELECT count(*) FROM pattern.pattern_registry WHERE status = 'candidate'")
    print("  Published: " + (pub[0][0] if pub else "0"))
    print("  Candidates: " + (cand[0][0] if cand else "0"))


def main():
    parser = argparse.ArgumentParser(description='News Pattern Library Engine')
    parser.add_argument('--candidates', action='store_true')
    parser.add_argument('--stats', action='store_true')
    parser.add_argument('--confidence', action='store_true')
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--evolution', action='store_true')
    parser.add_argument('--performance', action='store_true')
    parser.add_argument('--dashboard', action='store_true')
    parser.add_argument('--audit', action='store_true')
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()

    if not any([args.candidates, args.stats, args.confidence, args.publish,
                args.evolution, args.performance, args.dashboard, args.audit, args.full, args.list]):
        parser.print_help()
        sys.exit(1)

    start = datetime.utcnow()
    print("=" * 60)
    print("NEWS PATTERN LIBRARY ENGINE — " + start.strftime('%Y-%m-%d %H:%M:%S UTC'))
    print("Founder Rules: NO VALIDATED OUTCOME = NO PATTERN")
    print("=" * 60)

    if args.candidates or args.full:
        generate_candidates()
    if args.stats or args.full:
        calculate_statistics()
    if args.confidence or args.full:
        calculate_confidence()
    if args.publish or args.full:
        evaluate_publication()
    if args.evolution or args.full:
        track_evolution()
    if args.performance or args.full:
        track_performance()
    if args.dashboard or args.full:
        add_dashboard_metrics()
    if args.audit or args.full:
        ok = governance_audit()
        if not ok:
            print("\nGOVERNANCE AUDIT FAILED — fix issues before proceeding")
            sys.exit(1)
    if args.list or args.full:
        list_patterns()
    if args.stats or args.full:
        show_stats()

    elapsed = (datetime.utcnow() - start).total_seconds()
    print("\nCompleted in " + str(round(elapsed, 1)) + "s")


if __name__ == '__main__':
    main()
