#!/usr/bin/env python3
"""
Knowledge Quality Scoring Engine
=================================
Scores every record across all 5 registries on a 100-point scale.

Five categories × 20 points each:
  1. Evidence Score (0-20)
  2. Impact Score (0-20)
  3. Reuse Score (0-20)
  4. Confidence Score (0-20)
  5. Actionability Score (0-20)

Usage:
    python3 knowledge_scoring.py --backfill
    python3 knowledge_scoring.py --score <schema> <id>
    python3 knowledge_scoring.py --top-knowledge
    python3 knowledge_scoring.py --top-failures
    python3 knowledge_scoring.py --top-lessons
    python3 knowledge_scoring.py --top-decisions
    python3 knowledge_scoring.py --top-memories
    python3 knowledge_scoring.py --distribution
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone
from typing import Optional

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip3 install psycopg2-binary")
    sys.exit(1)


# ============================================================
# Grade System
# ============================================================

def calculate_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 95: return "A+"
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


# ============================================================
# Scoring Functions
# ============================================================

def score_evidence(row: dict, schema: str) -> float:
    """
    Evidence Score (0-20):
    Evaluate: logs, screenshots, DB evidence, verification, git commits, audit reports.
    """
    score = 0.0
    text = json.dumps(row, default=str).lower()
    
    # Has verification text
    verification = row.get("verification", "") or ""
    if verification and len(str(verification).strip()) > 10:
        score += 5
    
    # Has evidence data (JSONB)
    evidence = row.get("evidence", None)
    if evidence and evidence != {} and evidence != "null":
        score += 4
    
    # Has fix applied
    fix = row.get("fix_applied", "") or ""
    if fix and len(str(fix).strip()) > 10:
        score += 3
    
    # Has source reference
    source = row.get("source", "") or ""
    if source and source not in ["manual", "unknown", ""]:
        score += 2
    
    # Enrichment bonus: enriched content detected
    source_str = str(source)
    if "enrichment" in source_str or "rcaf" in source_str:
        score += 2
    
    # Has content/detail
    content = row.get("content", "") or row.get("key_takeaways", "") or row.get("memory_value", "")
    if content:
        content_str = json.dumps(content, default=str) if isinstance(content, (dict, list)) else str(content)
        if len(content_str) > 50:
            score += 3
    
    # Has summary
    summary = row.get("summary", "") or ""
    if summary and len(str(summary).strip()) > 20:
        score += 2
    
    # Has preventive rule (for failures)
    preventive = row.get("preventive_rule", "") or ""
    if preventive and len(str(preventive).strip()) > 10:
        score += 1
    
    return min(score, 20.0)


def score_impact(row: dict, schema: str) -> float:
    """
    Impact Score (0-20):
    Based on severity or importance of the record.
    """
    # For failures: use severity
    if schema == "failure":
        severity = (row.get("severity", "") or "").lower()
        return {"critical": 20, "high": 15, "medium": 10, "low": 5}.get(severity, 8)
    
    # For lessons: based on confidence and linkage
    if schema == "lesson":
        score = 8  # base
        if row.get("related_failure_id"):
            score += 4  # linked to a failure = higher impact
        if row.get("related_decision_id"):
            score += 2
        conf = float(row.get("confidence_score", 0) or 0)
        score += int(conf * 6)
        return min(score, 20.0)
    
    # For decisions: based on status
    if schema == "decision":
        status = (row.get("status", "") or "").lower()
        base = {"validated": 16, "executed": 14, "pending": 8, "reverted": 6}.get(status, 8)
        return min(base, 20.0)
    
    # For knowledge: based on category importance
    if schema == "knowledge":
        cat = (row.get("category", "") or "").lower()
        base = {"architecture": 14, "security": 15, "infrastructure": 13}.get(cat, 10)
        conf = float(row.get("confidence_score", 0) or 0)
        base += int(conf * 6)
        return min(base, 20.0)
    
    # For agent memory: based on memory type
    if schema == "agent":
        mt = (row.get("memory_type", "") or "").lower()
        base = {"constraint": 16, "correction": 14, "workflow": 12, "convention": 11,
                "capability": 10, "preference": 8, "environment": 8}.get(mt, 8)
        return min(base, 20.0)
    
    return 10.0


def score_reuse(row: dict, schema: str) -> float:
    """
    Reuse Score (0-20):
    Can this knowledge prevent future failures? Become a SOP/playbook/rule?
    """
    score = 0.0
    
    # Preventive rule exists
    preventive = row.get("preventive_rule", "") or ""
    if preventive and len(str(preventive).strip()) > 10:
        score += 8
    
    # Has fix that could be a playbook
    fix = row.get("fix_applied", "") or ""
    if fix and len(str(fix).strip()) > 10:
        score += 4
    
    # Has root cause (reusable diagnosis)
    rc = row.get("root_cause", "") or ""
    if rc and len(str(rc).strip()) > 10:
        score += 3
    
    # Has key takeaways or structured content
    kt = row.get("key_takeaways", None)
    if kt and kt != "null":
        score += 3
    
    # Has summary suitable for SOP
    summary = row.get("summary", "") or ""
    if summary and len(str(summary).strip()) > 30:
        score += 2
    
    # Agent memory with constraint type = reusable rule
    if schema == "agent" and (row.get("memory_type", "") or "").lower() == "constraint":
        score += 6
        # Enriched constraint with rule + SOP = extra reuse
        mv = row.get("memory_value", {})
        if isinstance(mv, dict) and "enrichment" in mv:
            score += 4
    
    # Knowledge with good content
    if schema == "knowledge":
        content = row.get("content", "")
        if content:
            score += 4
    
    # Linked records = more reusable
    if row.get("related_failure_id") or row.get("related_decision_id"):
        score += 2
    
    return min(score, 20.0)


def score_confidence(row: dict, schema: str) -> float:
    """
    Confidence Score (0-20):
    Assumption → Partial → Verified → Multi-source → Fully Proven
    """
    # Use existing confidence_score as base (0-1 scale → 0-12)
    existing = float(row.get("confidence_score", 0) or 0)
    score = existing * 12
    
    # Bonus for verification text
    verification = row.get("verification", "") or ""
    if verification and len(str(verification).strip()) > 10:
        score += 4
    
    # Bonus for having a source
    source = row.get("source", "") or ""
    if source and source not in ["manual", "unknown", ""]:
        score += 2
    
    # Enriched records get confidence boost
    if row.get("quality_last_updated"):
        score += 2
    
    # Bonus for resolved status (failures)
    status = (row.get("status", "") or "").lower()
    if status in ["resolved", "verified", "validated", "active"]:
        score += 2
    
    return min(score, 20.0)


def score_actionability(row: dict, schema: str) -> float:
    """
    Actionability Score (0-20):
    Fix exists? SOP exists? Rule exists? Prevention exists? Repeatable process?
    """
    score = 0.0
    
    # Fix exists and is detailed
    fix = row.get("fix_applied", "") or ""
    if fix and len(str(fix).strip()) > 10:
        score += 5
    if fix and len(str(fix).strip()) > 50:
        score += 2
    
    # Preventive rule exists
    preventive = row.get("preventive_rule", "") or ""
    if preventive and len(str(preventive).strip()) > 10:
        score += 5
    
    # Verification exists (proves fix works)
    verification = row.get("verification", "") or ""
    if verification and len(str(verification).strip()) > 10:
        score += 3
    
    # Has root cause (can diagnose again)
    rc = row.get("root_cause", "") or ""
    if rc and len(str(rc).strip()) > 10:
        score += 2
    
    # Agent memory with constraint = actionable rule
    if schema == "agent" and (row.get("memory_type", "") or "").lower() == "constraint":
        score += 6
        # Enriched with SOP = extra actionability
        mv = row.get("memory_value", {})
        if isinstance(mv, dict) and "enrichment" in mv:
            score += 4
    
    # Decision with outcome = proven actionable
    if schema == "decision":
        if (row.get("actual_outcome", "") or ""):
            score += 4
        if (row.get("chosen_option", "") or ""):
            score += 2
    
    # Knowledge with actionable content
    if schema == "knowledge":
        content = row.get("content", "")
        if content:
            score += 3
    
    # Lesson with takeaways
    if schema == "lesson":
        kt = row.get("key_takeaways", None)
        if kt and kt != "null":
            score += 3
    
    return min(score, 20.0)


# ============================================================
# Master Scoring
# ============================================================

def score_record(row: dict, schema: str) -> dict:
    """
    Calculate all 5 scores and total for a single record.
    Returns dict with all score fields.
    """
    evidence = score_evidence(row, schema)
    impact = score_impact(row, schema)
    reuse = score_reuse(row, schema)
    confidence = score_confidence(row, schema)
    actionability = score_actionability(row, schema)
    
    total = evidence + impact + reuse + confidence + actionability
    grade = calculate_grade(total)
    
    return {
        "quality_score": round(total, 1),
        "quality_grade": grade,
        "evidence_score": round(evidence, 1),
        "impact_score": round(impact, 1),
        "reuse_score": round(reuse, 1),
        "q_confidence_score": round(confidence, 1),
        "actionability_score": round(actionability, 1),
        "quality_last_updated": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# Database Operations
# ============================================================

SCHEMA_TABLES = {
    "knowledge": ("knowledge_registry", "knowledge"),
    "decision": ("decision_registry", "decision"),
    "failure": ("failure_registry", "failure"),
    "lesson": ("lesson_registry", "lesson"),
    "agent": ("agent_memory_registry", "agent"),
}


class KnowledgeScorer:
    """Score all records in the Knowledge OS database."""
    
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            dbname=os.environ.get("POSTGRES_DB", "knowledge_os"),
            user=os.environ.get("POSTGRES_USER", "knowledge_admin"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
        )
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def backfill_all(self) -> dict:
        """Score every record across all registries."""
        results = {}
        for schema_name, (table_name, _) in SCHEMA_TABLES.items():
            result = self._score_registry(schema_name, table_name)
            results[schema_name] = result
        return results
    
    def _score_registry(self, schema: str, table: str) -> dict:
        """Score all records in a single registry."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {schema}.{table} ORDER BY created_at")
            rows = cur.fetchall()
        
        scored = 0
        for row in rows:
            row_dict = dict(row)
            scores = score_record(row_dict, schema)
            
            with self.conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE {schema}.{table}
                    SET quality_score = %s,
                        quality_grade = %s,
                        evidence_score = %s,
                        impact_score = %s,
                        reuse_score = %s,
                        q_confidence_score = %s,
                        actionability_score = %s,
                        quality_last_updated = %s
                    WHERE id = %s
                """, (
                    scores["quality_score"], scores["quality_grade"],
                    scores["evidence_score"], scores["impact_score"],
                    scores["reuse_score"], scores["q_confidence_score"],
                    scores["actionability_score"], scores["quality_last_updated"],
                    row_dict["id"]
                ))
                scored += 1
        
        self.conn.commit()
        return {"schema": schema, "table": table, "records_scored": scored}
    
    def score_single(self, schema: str, record_id: str) -> dict:
        """Score a single record by ID."""
        table = SCHEMA_TABLES.get(schema, (None, None))[0]
        if not table:
            return {"error": f"Unknown schema: {schema}"}
        
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {schema}.{table} WHERE id = %s", (record_id,))
            row = cur.fetchone()
        
        if not row:
            return {"error": f"Record {record_id} not found in {schema}.{table}"}
        
        scores = score_record(dict(row), schema)
        
        with self.conn.cursor() as cur:
            cur.execute(f"""
                UPDATE {schema}.{table}
                SET quality_score = %s, quality_grade = %s,
                    evidence_score = %s, impact_score = %s,
                    reuse_score = %s, q_confidence_score = %s,
                    actionability_score = %s, quality_last_updated = %s
                WHERE id = %s
            """, (
                scores["quality_score"], scores["quality_grade"],
                scores["evidence_score"], scores["impact_score"],
                scores["reuse_score"], scores["q_confidence_score"],
                scores["actionability_score"], scores["quality_last_updated"],
                record_id
            ))
        self.conn.commit()
        return {"record_id": record_id, "schema": schema, "scores": scores}
    
    def top_records(self, schema: str, limit: int = 10) -> list:
        """Get top-scored records for a schema."""
        table = SCHEMA_TABLES[schema][0]
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT id, quality_score, quality_grade,
                       evidence_score, impact_score, reuse_score,
                       q_confidence_score, actionability_score, created_at
                FROM {schema}.{table}
                ORDER BY quality_score DESC NULLS LAST
                LIMIT %s
            """, (limit,))
            return [dict(r) for r in cur.fetchall()]
    
    def quality_distribution(self) -> dict:
        """Get quality distribution across all registries."""
        dist = {}
        for schema_name, (table_name, _) in SCHEMA_TABLES.items():
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"""
                    SELECT 
                        quality_grade,
                        count(*) as count,
                        round(avg(quality_score), 1) as avg_score,
                        round(min(quality_score), 1) as min_score,
                        round(max(quality_score), 1) as max_score
                    FROM {schema_name}.{table_name}
                    GROUP BY quality_grade
                    ORDER BY avg_score DESC
                """)
                dist[schema_name] = [dict(r) for r in cur.fetchall()]
        return dist
    
    def total_counts(self) -> dict:
        """Get total records per registry."""
        counts = {}
        for schema_name, (table_name, _) in SCHEMA_TABLES.items():
            with self.conn.cursor() as cur:
                cur.execute(f"SELECT count(*) FROM {schema_name}.{table_name}")
                counts[schema_name] = cur.fetchone()[0]
        return counts
    
    def all_scored_check(self) -> dict:
        """Verify all records have been scored."""
        check = {}
        for schema_name, (table_name, _) in SCHEMA_TABLES.items():
            with self.conn.cursor() as cur:
                cur.execute(f"""
                    SELECT 
                        count(*) as total,
                        count(quality_score) as scored,
                        count(*) - count(quality_score) as unscored
                    FROM {schema_name}.{table_name}
                """)
                row = cur.fetchone()
                check[schema_name] = {
                    "total": row[0], "scored": row[1], "unscored": row[2],
                    "coverage": f"{row[1]}/{row[0]}" if row[0] > 0 else "0/0"
                }
        return check


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Knowledge Quality Scoring Engine")
    parser.add_argument("--backfill", action="store_true", help="Score all records")
    parser.add_argument("--score", nargs=2, metavar=("SCHEMA", "ID"), help="Score a single record")
    parser.add_argument("--top-knowledge", action="store_true", help="Top knowledge records")
    parser.add_argument("--top-failures", action="store_true", help="Top failure records")
    parser.add_argument("--top-lessons", action="store_true", help="Top lesson records")
    parser.add_argument("--top-decisions", action="store_true", help="Top decision records")
    parser.add_argument("--top-memories", action="store_true", help="Top agent memory records")
    parser.add_argument("--distribution", action="store_true", help="Quality distribution")
    parser.add_argument("--check", action="store_true", help="Verify all records scored")
    parser.add_argument("--limit", type=int, default=10, help="Limit for top queries")
    args = parser.parse_args()
    
    scorer = KnowledgeScorer()
    
    try:
        if args.backfill:
            print("=== BACKFILL: Scoring all records ===")
            results = scorer.backfill_all()
            total = sum(r["records_scored"] for r in results.values())
            print(f"\nTotal records scored: {total}")
            for schema, r in results.items():
                print(f"  {schema}: {r['records_scored']} records")
        
        elif args.score:
            schema, record_id = args.score
            result = scorer.score_single(schema, record_id)
            print(json.dumps(result, indent=2, default=str))
        
        elif args.top_knowledge:
            print(json.dumps(scorer.top_records("knowledge", args.limit), indent=2, default=str))
        elif args.top_failures:
            print(json.dumps(scorer.top_records("failure", args.limit), indent=2, default=str))
        elif args.top_lessons:
            print(json.dumps(scorer.top_records("lesson", args.limit), indent=2, default=str))
        elif args.top_decisions:
            print(json.dumps(scorer.top_records("decision", args.limit), indent=2, default=str))
        elif args.top_memories:
            print(json.dumps(scorer.top_records("agent", args.limit), indent=2, default=str))
        
        elif args.distribution:
            dist = scorer.quality_distribution()
            print(json.dumps(dist, indent=2, default=str))
        
        elif args.check:
            check = scorer.all_scored_check()
            counts = scorer.total_counts()
            print("=== SCORING COVERAGE CHECK ===")
            total_records = 0
            total_scored = 0
            for schema, info in check.items():
                total_records += info["total"]
                total_scored += info["scored"]
                status = "✅" if info["unscored"] == 0 else "❌"
                print(f"  {status} {schema:12s}: {info['coverage']} scored ({info['total']} total)")
            print(f"\n  Total: {total_scored}/{total_records} records scored")
        
        else:
            parser.print_help()
    
    finally:
        scorer.close()


if __name__ == "__main__":
    main()
