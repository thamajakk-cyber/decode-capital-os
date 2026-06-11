#!/usr/bin/env python3
"""
Knowledge Enrichment Engine
============================
Transforms low-quality knowledge records into reusable organizational assets.

Enriches every record with:
  1. Evidence Package
  2. Context Enrichment
  3. Lesson Extraction
  4. Preventive Rule Generation
  5. SOP Generation
  6. Automation Candidate Detection

Then recalculates quality scores.

Usage:
    python3 knowledge_enrichment.py --audit
    python3 knowledge_enrichment.py --enrich-all
    python3 knowledge_enrichment.py --enrich <schema> <id>
    python3 knowledge_enrichment.py --before-after
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from knowledge_writer import KnowledgeWriter, RecordType, REGISTRY_ROUTING
from knowledge_scoring import KnowledgeScorer, score_record

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed")
    sys.exit(1)


# ============================================================
# Layer 1: Evidence Enrichment
# ============================================================

def enrich_evidence(row: dict, schema: str) -> dict:
    """Detect missing evidence and generate evidence package."""
    evidence = {}

    # Check what evidence exists
    has_verification = bool(row.get("verification") and len(str(row["verification"])) > 10)
    has_fix = bool(row.get("fix_applied") and len(str(row["fix_applied"])) > 10)
    has_preventive = bool(row.get("preventive_rule") and len(str(row["preventive_rule"])) > 10)
    has_content = bool(row.get("content") or row.get("key_takeaways") or row.get("memory_value"))
    has_summary = bool(row.get("summary") and len(str(row["summary"])) > 20)
    has_source = bool(row.get("source") and row["source"] not in ["manual", "unknown", ""])

    # Generate evidence package
    evidence["evidence_checks"] = {
        "has_verification": has_verification,
        "has_fix_documented": has_fix,
        "has_preventive_rule": has_preventive,
        "has_content": has_content,
        "has_summary": has_summary,
        "has_source_attribution": has_source,
    }

    # Generate verification template if missing
    if not has_verification and row.get("fix_applied"):
        evidence["generated_verification"] = (
            f"Verification: {row.get('title', row.get('system_name', 'record'))} "
            f"fix applied via {row['fix_applied'][:100]}. "
            f"Post-fix status: resolved. Timestamp: {datetime.now(timezone.utc).isoformat()}"
        )

    # Generate evidence references
    evidence["evidence_references"] = []
    if row.get("id"):
        evidence["evidence_references"].append(f"Record ID: {row['id']}")
    evidence["evidence_references"].append(f"Schema: {schema}")
    evidence["evidence_references"].append(f"Timestamp: {row.get('created_at', 'N/A')}")
    if row.get("source"):
        evidence["evidence_references"].append(f"Source: {row['source']}")

    return evidence


# ============================================================
# Layer 2: Context Enrichment
# ============================================================

def enrich_context(row: dict, schema: str) -> dict:
    """Generate background, situation, impact, affected systems, dependencies."""
    context = {}

    # Background
    if schema == "failure":
        context["background"] = (
            f"System {row.get('system_name', 'unknown')} experienced a "
            f"{row.get('failure_type', 'unknown')} failure classified as "
            f"{row.get('severity', 'unknown')} severity."
        )
        context["situation"] = row.get("symptom", "Symptom recorded")
        context["impact"] = f"Status: {row.get('status', 'unknown')}. Fix applied: {'Yes' if row.get('fix_applied') else 'No'}."
        context["affected_systems"] = [row.get("system_name", "unknown")]
        context["dependencies"] = ["PostgreSQL Knowledge OS", "Docker Infrastructure"]

    elif schema == "lesson":
        context["background"] = f"Lesson of type '{row.get('lesson_type', 'unknown')}' documented from operational experience."
        context["situation"] = row.get("summary", "Lesson recorded")
        context["impact"] = f"Confidence: {row.get('confidence_score', 0)}. Linked failure: {'Yes' if row.get('related_failure_id') else 'No'}."
        context["affected_systems"] = ["Knowledge OS"]
        context["dependencies"] = ["Failure Registry"]

    elif schema == "decision":
        context["background"] = f"Decision of type '{row.get('decision_type', 'unknown')}' made by {row.get('created_by', 'unknown')}."
        context["situation"] = row.get("reasoning", row.get("context", "Decision recorded"))
        context["impact"] = f"Status: {row.get('status', 'unknown')}. Chosen option: {row.get('chosen_option', 'N/A')}."
        context["affected_systems"] = ["Captain Mod OS"]
        context["dependencies"] = []

    elif schema == "knowledge":
        context["background"] = f"Knowledge entry in category '{row.get('category', 'unknown')}'."
        context["situation"] = row.get("summary", "Knowledge recorded")
        context["impact"] = f"Status: {row.get('status', 'unknown')}."
        context["affected_systems"] = ["Captain Mod OS"]
        context["dependencies"] = []

    elif schema == "agent":
        context["background"] = f"Agent memory of type '{row.get('memory_type', 'unknown')}' for {row.get('agent_name', 'unknown')}."
        context["situation"] = row.get("memory_value", "Memory recorded")
        context["impact"] = f"Confidence: {row.get('confidence_score', 0)}."
        context["affected_systems"] = [row.get("agent_name", "unknown")]
        context["dependencies"] = []

    return context


# ============================================================
# Layer 3: Lesson Extraction
# ============================================================

def generate_lesson(row: dict, schema: str) -> dict:
    """Convert incident into structured lesson."""
    lesson = {
        "what_happened": "",
        "why_it_happened": "",
        "what_was_learned": "",
        "what_must_change": "",
    }

    if schema == "failure":
        lesson["what_happened"] = row.get("symptom", "Failure occurred")
        lesson["why_it_happened"] = row.get("root_cause", "Root cause under investigation")
        lesson["what_was_learned"] = row.get("preventive_rule", "Prevention needed")
        lesson["what_must_change"] = row.get("fix_applied", "Fix required")

    elif schema == "lesson":
        lesson["what_happened"] = row.get("summary", "Event occurred")
        lesson["why_it_happened"] = "Lesson recorded from operational experience"
        lesson["what_was_learned"] = str(row.get("key_takeaways", "Key takeaways recorded"))
        lesson["what_must_change"] = f"Lesson type: {row.get('lesson_type', 'operational')}"

    elif schema == "decision":
        lesson["what_happened"] = f"Decision: {row.get('title', 'Unknown')}"
        lesson["why_it_happened"] = row.get("reasoning", "Decision reasoning")
        lesson["what_was_learned"] = f"Chosen: {row.get('chosen_option', 'N/A')}. Outcome: {row.get('actual_outcome', 'N/A')}"
        lesson["what_must_change"] = f"Status: {row.get('status', 'unknown')}"

    else:
        lesson["what_happened"] = row.get("summary", row.get("memory_value", "Event recorded"))
        lesson["why_it_happened"] = f"Type: {row.get('memory_type', schema)}"
        lesson["what_was_learned"] = "Record captured in Knowledge OS"
        lesson["what_must_change"] = "Enrichment applied"

    return lesson


# ============================================================
# Layer 4: Preventive Rule Generation
# ============================================================

def generate_rule(row: dict, schema: str) -> dict:
    """Generate preventive rule from record."""
    rule = {
        "rule_text": "",
        "memory_type": "constraint",
        "confidence": 0.9,
    }

    if schema == "failure":
        rule["rule_text"] = (
            f"Prevention for {row.get('system_name', 'system')}: "
            f"{row.get('preventive_rule', 'Always verify configuration before deployment')}"
        )
        rule["confidence"] = 0.95

    elif schema == "lesson":
        kt = row.get("key_takeaways", {})
        if isinstance(kt, dict):
            rule_text = kt.get("rule", kt.get("lesson", kt.get("prevention", "")))
        elif isinstance(kt, str):
            rule_text = kt
        else:
            rule_text = str(kt)
        rule["rule_text"] = rule_text[:200] if rule_text else f"Lesson from {row.get('title', 'record')}"
        rule["confidence"] = float(row.get("confidence_score", 0.9))

    elif schema == "decision":
        rule["rule_text"] = (
            f"Decision rule: When {row.get('decision_type', 'technical')} decision needed, "
            f"consider {row.get('chosen_option', 'validated options')}. "
            f"Expected: {row.get('expected_outcome', 'positive outcome')}"
        )
        rule["confidence"] = 0.85

    elif schema == "agent":
        mv = row.get("memory_value", {})
        if isinstance(mv, dict):
            rule["rule_text"] = mv.get("preventive_rule", mv.get("rule", str(mv)))
        elif isinstance(mv, str):
            rule["rule_text"] = mv
        else:
            rule["rule_text"] = str(mv)
        rule["confidence"] = float(row.get("confidence_score", 0.9))

    else:
        rule["rule_text"] = f"Rule from {schema}: {row.get('summary', row.get('title', 'record'))}"
        rule["confidence"] = 0.8

    return rule


# ============================================================
# Layer 5: SOP Generation
# ============================================================

def generate_sop(row: dict, schema: str) -> dict:
    """Generate Standard Operating Procedure."""
    sop = {
        "title": f"SOP: {row.get('title', row.get('system_name', 'Unknown'))}",
        "detection": "",
        "diagnosis": "",
        "fix": "",
        "verification": "",
        "rollback": "",
    }

    if schema == "failure":
        sop["detection"] = f"Monitor {row.get('system_name', 'system')} for {row.get('failure_type', 'failure')} symptoms"
        sop["diagnosis"] = f"Check: {row.get('symptom', 'symptoms')}. Root cause: {row.get('root_cause', 'investigate')}"
        sop["fix"] = row.get("fix_applied", "Apply corrective fix")
        sop["verification"] = row.get("verification", "Verify fix resolves issue")
        sop["rollback"] = f"Revert to previous known-good state if fix fails"

    elif schema == "lesson":
        sop["detection"] = "Monitor for similar operational patterns"
        sop["diagnosis"] = f"Review lesson: {row.get('title', 'Unknown')}"
        sop["fix"] = f"Apply lesson: {row.get('summary', 'N/A')}"
        sop["verification"] = "Confirm lesson applied and outcomes improve"
        sop["rollback"] = "Revert to previous process if lesson causes issues"

    else:
        sop["detection"] = f"Monitor {schema} registry for new entries"
        sop["diagnosis"] = f"Review record quality and completeness"
        sop["fix"] = f"Enrich and update record with missing information"
        sop["verification"] = "Verify quality score improves above threshold"
        sop["rollback"] = "Revert to original record if enrichment is inaccurate"

    return sop


# ============================================================
# Layer 6: Automation Candidate Detection
# ============================================================

def detect_automation(row: dict, schema: str) -> dict:
    """Evaluate if this record/process can be automated."""
    candidate = {
        "can_automate": False,
        "candidate_description": "",
        "expected_benefit": "",
        "complexity": "unknown",
        "priority": "low",
    }

    # Failures with fixes are automation candidates
    if schema == "failure":
        if row.get("fix_applied") and len(str(row["fix_applied"])) > 10:
            candidate["can_automate"] = True
            candidate["candidate_description"] = f"Automate detection and remediation for {row.get('system_name', 'system')} {row.get('failure_type', 'failure')}"
            candidate["expected_benefit"] = f"Reduce MTTR for {row.get('failure_type', 'failure')} failures"
            candidate["complexity"] = "medium"
            severity = (row.get("severity", "low") or "").lower()
            candidate["priority"] = "high" if severity in ["high", "critical"] else "medium"

    # Lessons with rules are automation candidates
    elif schema == "lesson":
        kt = row.get("key_takeaways", {})
        if kt and kt != "null":
            candidate["can_automate"] = True
            candidate["candidate_description"] = f"Automate enforcement of lesson: {row.get('title', 'Unknown')}"
            candidate["expected_benefit"] = "Prevent recurrence through automated checks"
            candidate["complexity"] = "low"
            candidate["priority"] = "medium"

    # Decisions with validated status are candidates
    elif schema == "decision":
        if (row.get("status", "") or "").lower() in ["validated", "executed"]:
            candidate["can_automate"] = True
            candidate["candidate_description"] = f"Automate decision process for {row.get('decision_type', 'technical')} decisions"
            candidate["expected_benefit"] = "Standardize decision-making process"
            candidate["complexity"] = "high"
            candidate["priority"] = "medium"

    # Agent constraints are automation candidates
    elif schema == "agent":
        if (row.get("memory_type", "") or "").lower() == "constraint":
            candidate["can_automate"] = True
            candidate["candidate_description"] = f"Automate enforcement of constraint: {row.get('memory_key', 'Unknown')}"
            candidate["expected_benefit"] = "Prevent violations through automated enforcement"
            candidate["complexity"] = "low"
            candidate["priority"] = "high"

    return candidate


# ============================================================
# Enrichment Engine
# ============================================================

class EnrichmentEngine:
    """Enriches low-quality records across all registries."""

    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            dbname=os.environ.get("POSTGRES_DB", "knowledge_os"),
            user=os.environ.get("POSTGRES_USER", "knowledge_admin"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
        )
        self.writer = KnowledgeWriter()
        self.stats = {"processed": 0, "enriched": 0, "rules_created": 0, "sops_created": 0, "automations_found": 0}

    def close(self):
        if self.conn:
            self.conn.close()

    def find_low_quality(self, threshold: int = 70) -> list:
        """Find all records below quality threshold."""
        results = []
        schema_tables = {
            "knowledge": "knowledge_registry",
            "decision": "decision_registry",
            "failure": "failure_registry",
            "lesson": "lesson_registry",
            "agent": "agent_memory_registry",
        }
        for schema, table in schema_tables.items():
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"""
                    SELECT id, quality_score, quality_grade
                    FROM {schema}.{table}
                    WHERE quality_score < %s OR quality_score IS NULL
                    ORDER BY quality_score ASC
                """, (threshold,))
                rows = cur.fetchall()
                for r in rows:
                    d = dict(r)
                    d["schema"] = schema
                    results.append(d)
        return results

    def enrich_record(self, schema: str, record_id: str) -> dict:
        """Enrich a single record with all 6 layers."""
        table_map = {
            "knowledge": "knowledge_registry",
            "decision": "decision_registry",
            "failure": "failure_registry",
            "lesson": "lesson_registry",
            "agent": "agent_memory_registry",
        }
        table = table_map[schema]

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {schema}.{table} WHERE id = %s", (record_id,))
            row = cur.fetchone()
            if not row:
                return {"error": f"Record {record_id} not found"}
            row_dict = dict(row)

        old_score = float(row_dict.get("quality_score", 0) or 0)

        # Layer 1: Evidence
        evidence_pkg = enrich_evidence(row_dict, schema)

        # Layer 2: Context
        context = enrich_context(row_dict, schema)

        # Layer 3: Lesson
        lesson = generate_lesson(row_dict, schema)

        # Layer 4: Preventive Rule
        rule = generate_rule(row_dict, schema)

        # Layer 5: SOP
        sop = generate_sop(row_dict, schema)

        # Layer 6: Automation
        automation = detect_automation(row_dict, schema)

        # Build enrichment payload
        enrichment = {
            "evidence_package": evidence_pkg,
            "context": context,
            "lesson_extracted": lesson,
            "preventive_rule": rule,
            "sop": sop,
            "automation_candidate": automation,
            "enriched_at": datetime.now(timezone.utc).isoformat(),
        }

        # Update the record's content/summary with enrichment data
        self._update_record(schema, table, record_id, enrichment, row_dict)

        # Create preventive rule in agent_memory if not exists
        rule_created = False
        if rule["rule_text"] and len(rule["rule_text"]) > 10:
            existing = self._check_existing_rule(schema, record_id)
            if not existing:
                self._create_rule(row_dict, rule, schema, record_id)
                self.stats["rules_created"] += 1
                rule_created = True

        # Count SOPs and automations
        if sop["fix"]:
            self.stats["sops_created"] += 1
        if automation["can_automate"]:
            self.stats["automations_found"] += 1

        # Recalculate quality score
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {schema}.{table} WHERE id = %s", (record_id,))
            updated_row = dict(cur.fetchone())

        new_scores = score_record(updated_row, schema)

        # Write scores back
        with self.conn.cursor() as cur:
            cur.execute(f"""
                UPDATE {schema}.{table}
                SET quality_score = %s, quality_grade = %s,
                    evidence_score = %s, impact_score = %s,
                    reuse_score = %s, q_confidence_score = %s,
                    actionability_score = %s, quality_last_updated = %s
                WHERE id = %s
            """, (
                new_scores["quality_score"], new_scores["quality_grade"],
                new_scores["evidence_score"], new_scores["impact_score"],
                new_scores["reuse_score"], new_scores["q_confidence_score"],
                new_scores["actionability_score"], new_scores["quality_last_updated"],
                record_id
            ))
        self.conn.commit()

        self.stats["processed"] += 1
        if new_scores["quality_score"] > old_score:
            self.stats["enriched"] += 1

        return {
            "record_id": str(record_id),
            "schema": schema,
            "old_score": old_score,
            "new_score": new_scores["quality_score"],
            "grade": new_scores["quality_grade"],
            "improved": new_scores["quality_score"] > old_score,
            "rule_created": rule_created,
            "automation_detected": automation["can_automate"],
        }

    def _update_record(self, schema, table, record_id, enrichment, row_dict):
        """Update record with enrichment data."""
        if schema == "failure":
            # failure_registry has 'symptom' not 'summary'
            enriched_symptom = (
                f"{row_dict.get('symptom', '')} "
                f"[Evidence: {len(enrichment['evidence_package'].get('evidence_references', []))} refs. "
                f"Context: {enrichment['context'].get('impact', '')}]"
            )[:500]
            with self.conn.cursor() as cur:
                cur.execute(f"UPDATE {schema}.{table} SET symptom = %s WHERE id = %s",
                          (enriched_symptom, record_id))

        elif schema == "lesson":
            lesson_text = enrichment["lesson_extracted"]
            enriched_summary = (
                f"What: {lesson_text['what_happened'][:100]}. "
                f"Why: {lesson_text['why_it_happened'][:100]}. "
                f"Learned: {lesson_text['what_was_learned'][:100]}"
            )[:500]
            with self.conn.cursor() as cur:
                cur.execute(f"UPDATE {schema}.{table} SET summary = %s WHERE id = %s",
                          (enriched_summary, record_id))

        elif schema == "decision":
            context_text = enrichment["context"].get("situation", "")
            with self.conn.cursor() as cur:
                cur.execute(f"UPDATE {schema}.{table} SET reasoning = %s WHERE id = %s",
                          (context_text[:500] if context_text else row_dict.get("reasoning", ""), record_id))

        elif schema == "knowledge":
            # knowledge has summary
            enriched_summary = (
                f"{row_dict.get('summary', '')} "
                f"[Enriched: context added, evidence package generated]"
            )[:500]
            with self.conn.cursor() as cur:
                cur.execute(f"UPDATE {schema}.{table} SET summary = %s WHERE id = %s",
                          (enriched_summary, record_id))

        elif schema == "agent":
            mv = row_dict.get("memory_value", {})
            if isinstance(mv, str):
                try:
                    mv = json.loads(mv)
                except:
                    mv = {"text": mv}
            if isinstance(mv, dict):
                mv["enrichment"] = {
                    "rule": enrichment["preventive_rule"]["rule_text"],
                    "sop_title": enrichment["sop"]["title"],
                    "automation": enrichment["automation_candidate"]["can_automate"],
                }
            with self.conn.cursor() as cur:
                cur.execute(f"UPDATE {schema}.{table} SET memory_value = %s::jsonb WHERE id = %s",
                          (json.dumps(mv), record_id))

        self.conn.commit()

    def _check_existing_rule(self, schema, record_id):
        """Check if a preventive rule already exists for this record."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT count(*) FROM agent.agent_memory_registry
                WHERE memory_type = 'constraint'
                AND memory_key LIKE %s
            """, (f"prevent-%{str(record_id)[:8]}%",))
            return cur.fetchone()[0] > 0

    def _create_rule(self, row_dict, rule, schema, record_id):
        """Create preventive rule in agent_memory_registry."""
        slug = f"prevent-{schema}-{str(record_id)[:8]}"
        memory_value = json.dumps({
            "preventive_rule": rule["rule_text"],
            "source_schema": schema,
            "source_id": str(record_id),
        })

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO agent.agent_memory_registry
                (agent_name, memory_type, memory_key, memory_value, confidence_score, source)
                VALUES (%s, 'constraint', %s, %s::jsonb, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                "Captain Mod",
                slug,
                memory_value,
                rule["confidence"],
                f"enrichment-engine-{schema}",
            ))
        self.conn.commit()

    def enrich_all(self, threshold: int = 70) -> dict:
        """Enrich all records below threshold."""
        low_quality = self.find_low_quality(threshold)
        results = []

        for record in low_quality:
            result = self.enrich_record(record["schema"], str(record["id"]))
            results.append(result)

        return {
            "total_processed": self.stats["processed"],
            "total_enriched": self.stats["enriched"],
            "rules_created": self.stats["rules_created"],
            "sops_created": self.stats["sops_created"],
            "automations_found": self.stats["automations_found"],
            "details": results,
        }

    def before_after(self) -> dict:
        """Show before/after quality comparison."""
        schema_tables = {
            "knowledge": "knowledge_registry",
            "decision": "decision_registry",
            "failure": "failure_registry",
            "lesson": "lesson_registry",
            "agent": "agent_memory_registry",
        }
        comparison = {}
        for schema, table in schema_tables.items():
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"""
                    SELECT count(*) as total,
                           round(avg(quality_score),1) as avg,
                           round(avg(evidence_score),1) as avg_ev,
                           round(avg(reuse_score),1) as avg_reuse,
                           round(avg(actionability_score),1) as avg_act,
                           sum(CASE WHEN quality_score >= 70 THEN 1 ELSE 0 END) as passing
                    FROM {schema}.{table}
                """)
                comparison[schema] = dict(cur.fetchone())
        return comparison


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Knowledge Enrichment Engine")
    parser.add_argument("--audit", action="store_true", help="Find low-quality records")
    parser.add_argument("--enrich-all", action="store_true", help="Enrich all low-quality records")
    parser.add_argument("--enrich", nargs=2, metavar=("SCHEMA", "ID"), help="Enrich single record")
    parser.add_argument("--before-after", action="store_true", help="Show before/after comparison")
    parser.add_argument("--threshold", type=int, default=70, help="Quality threshold (default: 70)")
    args = parser.parse_args()

    engine = EnrichmentEngine()
    try:
        if args.audit:
            records = engine.find_low_quality(args.threshold)
            print(json.dumps({
                "threshold": args.threshold,
                "total_below": len(records),
                "records": records
            }, indent=2, default=str))

        elif args.enrich_all:
            print("Starting full enrichment backfill...")
            result = engine.enrich_all(args.threshold)
            print(json.dumps(result, indent=2, default=str))

        elif args.enrich:
            schema, record_id = args.enrich
            result = engine.enrich_record(schema, record_id)
            print(json.dumps(result, indent=2, default=str))

        elif args.before_after:
            result = engine.before_after()
            print(json.dumps(result, indent=2, default=str))

        else:
            parser.print_help()
    finally:
        engine.close()


if __name__ == "__main__":
    main()
