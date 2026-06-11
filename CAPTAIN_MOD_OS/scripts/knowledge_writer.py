#!/usr/bin/env python3
"""
Knowledge Write Workflow Foundation
====================================
Converts events, incidents, decisions, lessons, and knowledge
into persistent Knowledge OS PostgreSQL records.

Usage:
    from knowledge_writer import KnowledgeWriter
    
    writer = KnowledgeWriter()
    
    # Write a knowledge record
    result = writer.write_knowledge(
        title="My Knowledge",
        summary="Short summary",
        content="Full content",
        category="architecture",
        source="manual"
    )
    
    # Write a failure
    result = writer.write_failure(
        system_name="service-x",
        failure_type="integration",
        severity="high",
        symptom="Connection timeout",
        root_cause="Network misconfiguration",
        fix_applied="Updated firewall rules"
    )
    
    # Auto-classify and route
    result = writer.write(
        record_type="LESSON",
        title="Lesson Title",
        summary="...",
        content="..."
    )
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip3 install psycopg2-binary")
    sys.exit(1)


# ============================================================
# Classification Engine
# ============================================================

class RecordType(Enum):
    KNOWLEDGE = "knowledge"
    DECISION = "decision"
    FAILURE = "failure"
    LESSON = "lesson"
    AGENT_MEMORY = "agent_memory"


# Classification rules: keyword → type
CLASSIFICATION_RULES = {
    RecordType.FAILURE: [
        "incident", "outage", "error", "failure", "crash", "bug",
        "broken", "down", "unavailable", "timeout", "crash", "conflict"
    ],
    RecordType.LESSON: [
        "lesson", "learned", "takeaway", "prevention", "never again",
        "always", "rule", "principle", "insight"
    ],
    RecordType.DECISION: [
        "decision", "chose", "selected", "decided", "alternative",
        "rationale", "trade-off", "option"
    ],
    RecordType.AGENT_MEMORY: [
        "agent", "memory", "preference", "capability", "config",
        "observation", "strategy", "context"
    ],
    RecordType.KNOWLEDGE: [
        "knowledge", "fact", "information", "reference", "documentation",
        "architecture", "blueprint", "guide"
    ],
}

# Routing: RecordType → (schema, table)
REGISTRY_ROUTING = {
    RecordType.KNOWLEDGE: ("knowledge", "knowledge_registry"),
    RecordType.DECISION: ("decision", "decision_registry"),
    RecordType.FAILURE: ("failure", "failure_registry"),
    RecordType.LESSON: ("lesson", "lesson_registry"),
    RecordType.AGENT_MEMORY: ("agent", "agent_memory_registry"),
}

# Allowed memory types for agent_memory_registry (matches DB CHECK constraint)
AGENT_MEMORY_TYPES = [
    "preference", "environment", "convention", "workflow",
    "correction", "capability", "constraint"
]


def classify_record(title: str, summary: str = "", content: str = "") -> RecordType:
    """
    Classify a record based on title, summary, and content keywords.
    Returns the most likely RecordType.
    """
    text = f"{title} {summary} {content}".lower()
    scores = {}
    
    for rtype, keywords in CLASSIFICATION_RULES.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[rtype] = score
    
    if not scores:
        return RecordType.KNOWLEDGE  # default
    
    return max(scores, key=scores.get)


# ============================================================
# Slug Generation
# ============================================================

def slugify(text: str) -> str:
    """Convert text to filesystem-safe slug."""
    import re
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:80].strip("-")


def generate_slug(title: str) -> str:
    """Generate a unique slug from title."""
    return slugify(title)


# ============================================================
# Knowledge Writer
# ============================================================

class KnowledgeWriter:
    """Writes records to PostgreSQL Knowledge OS registries."""
    
    def __init__(self, host=None, port=None, dbname=None, user=None, password=None):
        self.db_config = {
            "host": host or os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "port": int(port or os.environ.get("POSTGRES_PORT", "5432")),
            "dbname": dbname or os.environ.get("POSTGRES_DB", "knowledge_os"),
            "user": user or os.environ.get("POSTGRES_USER", "knowledge_admin"),
            "password": password or os.environ.get("POSTGRES_PASSWORD", ""),
        }
    
    def _connect(self):
        if not self.db_config["password"]:
            raise ValueError("POSTGRES_PASSWORD not set")
        return psycopg2.connect(**self.db_config)
    
    def write(self, record_type: str, title: str, summary: str = "",
              content: str = "", tags: list = None, source: str = "manual",
              **kwargs) -> dict:
        """
        Auto-classify and write a record to the correct registry.
        
        Args:
            record_type: KNOWLEDGE, DECISION, FAILURE, LESSON, or AGENT_MEMORY
            title: Record title
            summary: Short summary
            content: Full content
            tags: List of tags
            source: Source of the record
            **kwargs: Additional fields specific to the record type
        
        Returns:
            dict with record_id, schema, table, slug
        """
        rtype = RecordType(record_type.lower())
        schema, table = REGISTRY_ROUTING[rtype]
        slug = generate_slug(title)
        
        conn = self._connect()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if rtype == RecordType.KNOWLEDGE:
                    record_id = self._write_knowledge(cur, title, slug, summary, content, tags, source, **kwargs)
                elif rtype == RecordType.DECISION:
                    record_id = self._write_decision(cur, title, slug, summary, content, tags, source, **kwargs)
                elif rtype == RecordType.FAILURE:
                    record_id = self._write_failure(cur, title, slug, summary, content, tags, source, **kwargs)
                elif rtype == RecordType.LESSON:
                    record_id = self._write_lesson(cur, title, slug, summary, content, tags, source, **kwargs)
                elif rtype == RecordType.AGENT_MEMORY:
                    record_id = self._write_agent_memory(cur, title, slug, summary, content, tags, source, **kwargs)
            
            conn.commit()
            
            return {
                "status": "success",
                "record_id": str(record_id),
                "record_type": rtype.value,
                "schema": schema,
                "table": table,
                "slug": slug,
                "title": title,
            }
        
        except Exception as e:
            conn.rollback()
            return {
                "status": "error",
                "error": str(e),
                "record_type": rtype.value,
                "schema": schema,
                "table": table,
            }
        finally:
            conn.close()
    
    def _write_knowledge(self, cur, title, slug, summary, content, tags, source, **kwargs):
        # Ensure content is valid JSON for JSONB column
        if isinstance(content, str):
            content_json = json.dumps({"text": content})
        elif isinstance(content, (dict, list)):
            content_json = json.dumps(content)
        else:
            content_json = json.dumps({"text": str(content)})
        
        cur.execute("""
            INSERT INTO knowledge.knowledge_registry 
            (title, slug, category, subcategory, content, summary, source, tags, status, confidence_score)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            title, slug,
            kwargs.get("category", "general"),
            kwargs.get("subcategory", ""),
            content_json,
            summary,
            source,
            tags or [],
            kwargs.get("status", "active"),
            kwargs.get("confidence_score", 1.0),
        ))
        return cur.fetchone()["id"]
    
    def _jsonify(self, val):
        """Convert value to valid JSON string for JSONB columns."""
        if isinstance(val, str):
            try:
                json.loads(val)
                return val  # already valid JSON
            except (json.JSONDecodeError, TypeError):
                return json.dumps({"text": val})
        elif isinstance(val, (dict, list)):
            return json.dumps(val)
        elif val is None:
            return json.dumps(None)
        else:
            return json.dumps({"text": str(val)})

    # Allowed values for CHECK constraints
    DECISION_STATUSES = ["pending", "executed", "validated", "reverted"]
    DECISION_TYPES = ["operational", "strategic", "technical", "financial", "personnel"]
    FAILURE_TYPES = ["infrastructure", "application", "configuration", "integration", "security", "performance"]
    FAILURE_STATUSES = ["open", "investigating", "resolved", "verified", "prevented"]
    KNOWLEDGE_STATUSES = ["draft", "active", "archived", "deprecated"]

    def _write_decision(self, cur, title, slug, summary, content, tags, source, **kwargs):
        context_json = self._jsonify({"summary": summary, "tags": tags or []})
        reasoning_json = self._jsonify(content)
        alternatives_json = self._jsonify(kwargs.get("alternatives", []))
        
        cur.execute("""
            INSERT INTO decision.decision_registry
            (title, decision_type, context, reasoning, alternatives, chosen_option,
             expected_outcome, actual_outcome, status, created_by)
            VALUES (%s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            title,
            kwargs.get("decision_type", "technical"),
            context_json,
            reasoning_json,
            alternatives_json,
            kwargs.get("chosen_option", ""),
            kwargs.get("expected_outcome", summary),
            kwargs.get("actual_outcome", ""),
            kwargs.get("status", "executed"),  # CHECK: pending|executed|validated|reverted
            source,
        ))
        return cur.fetchone()["id"]
    
    def _write_failure(self, cur, title, slug, summary, content, tags, source, **kwargs):
        root_cause_json = self._jsonify(content)
        evidence_json = self._jsonify(kwargs.get("evidence", {}))
        
        cur.execute("""
            INSERT INTO failure.failure_registry
            (system_name, failure_type, severity, symptom, root_cause, evidence,
             fix_applied, verification, preventive_rule, status)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s)
            RETURNING id
        """, (
            kwargs.get("system_name", title),
            kwargs.get("failure_type", "application"),  # CHECK: infrastructure|application|configuration|integration|security|performance
            kwargs.get("severity", "medium"),
            summary,
            root_cause_json,
            evidence_json,
            kwargs.get("fix_applied", ""),
            kwargs.get("verification", ""),
            kwargs.get("preventive_rule", ""),
            kwargs.get("status", "resolved"),
        ))
        return cur.fetchone()["id"]
    
    def _write_lesson(self, cur, title, slug, summary, content, tags, source, **kwargs):
        key_takeaways_json = self._jsonify(content)
        
        cur.execute("""
            INSERT INTO lesson.lesson_registry
            (title, lesson_type, summary, key_takeaways, related_failure_id,
             related_decision_id, confidence_score)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s)
            RETURNING id
        """, (
            title,
            kwargs.get("lesson_type", "operational"),
            summary,
            key_takeaways_json,
            kwargs.get("related_failure_id"),
            kwargs.get("related_decision_id"),
            kwargs.get("confidence_score", 1.0),
        ))
        return cur.fetchone()["id"]
    
    def _write_agent_memory(self, cur, title, slug, summary, content, tags, source, **kwargs):
        memory_type = kwargs.get("memory_type", "observation")
        if memory_type not in AGENT_MEMORY_TYPES:
            raise ValueError(f"Invalid memory_type: {memory_type}. Must be one of: {AGENT_MEMORY_TYPES}")
        
        memory_value_json = self._jsonify(content)
        
        cur.execute("""
            INSERT INTO agent.agent_memory_registry
            (agent_name, memory_type, memory_key, memory_value, confidence_score, source)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s)
            RETURNING id
        """, (
            kwargs.get("agent_name", "hermes-default"),
            memory_type,
            slug,
            memory_value_json,
            kwargs.get("confidence_score", 1.0),
            source,
        ))
        return cur.fetchone()["id"]
    
    # ============================================================
    # Convenience Methods
    # ============================================================
    
    def write_knowledge(self, title, summary="", content="", category="general",
                        subcategory="", tags=None, source="manual", **kwargs):
        return self.write("knowledge", title, summary, content, tags, source,
                         category=category, subcategory=subcategory, **kwargs)
    
    def write_decision(self, title, summary="", content="", decision_type="technical",
                       alternatives=None, chosen_option="", expected_outcome="",
                       actual_outcome="", status="decided", source="manual", **kwargs):
        return self.write("decision", title, summary, content, None, source,
                         decision_type=decision_type, alternatives=alternatives or [],
                         chosen_option=chosen_option, expected_outcome=expected_outcome,
                         actual_outcome=actual_outcome, status=status, **kwargs)
    
    def write_failure(self, title, summary="", content="", system_name="",
                      failure_type="unknown", severity="medium", fix_applied="",
                      verification="", preventive_rule="", status="resolved",
                      source="manual", **kwargs):
        return self.write("failure", title, summary, content, None, source,
                         system_name=system_name or title, failure_type=failure_type,
                         severity=severity, fix_applied=fix_applied, verification=verification,
                         preventive_rule=preventive_rule, status=status, **kwargs)
    
    def write_lesson(self, title, summary="", content="", lesson_type="operational",
                     related_failure_id=None, related_decision_id=None,
                     confidence_score=1.0, source="manual", **kwargs):
        return self.write("lesson", title, summary, content, None, source,
                         lesson_type=lesson_type, related_failure_id=related_failure_id,
                         related_decision_id=related_decision_id,
                         confidence_score=confidence_score, **kwargs)
    
    def write_agent_memory(self, agent_name, memory_type, memory_key, memory_value,
                           context="", confidence_score=1.0, source="manual", **kwargs):
        return self.write("agent_memory", memory_key, context, memory_value, None, source,
                         agent_name=agent_name, memory_type=memory_type, **kwargs)
    
    def verify_record(self, record_id: str, schema: str, table: str) -> dict:
        """Verify a record exists and return its data."""
        conn = self._connect()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"SELECT * FROM {schema}.{table} WHERE id = %s", (record_id,))
                row = cur.fetchone()
                if row:
                    return {"exists": True, "data": dict(row)}
                return {"exists": False}
        finally:
            conn.close()
    
    def read_all(self, schema: str, table: str) -> list:
        """Read all records from a registry table."""
        conn = self._connect()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"SELECT * FROM {schema}.{table} ORDER BY created_at")
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        finally:
            conn.close()


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Knowledge OS Write Workflow")
    parser.add_argument("--type", choices=["KNOWLEDGE", "DECISION", "FAILURE", "LESSON", "AGENT_MEMORY"],
                       help="Record type")
    parser.add_argument("--title", required=True, help="Record title")
    parser.add_argument("--summary", default="", help="Short summary")
    parser.add_argument("--content", default="", help="Full content")
    parser.add_argument("--source", default="manual", help="Source")
    parser.add_argument("--verify", action="store_true", help="Verify after write")
    
    # Type-specific args
    parser.add_argument("--category", default="general", help="Knowledge category")
    parser.add_argument("--decision-type", default="technical", help="Decision type")
    parser.add_argument("--system-name", default="", help="Failure system name")
    parser.add_argument("--failure-type", default="application", help="Failure type")
    parser.add_argument("--severity", default="medium", help="Failure severity")
    parser.add_argument("--memory-type", default="observation", help="Agent memory type")
    parser.add_argument("--agent-name", default="hermes-default", help="Agent name")
    parser.add_argument("--fix-applied", default="", help="Failure fix applied")
    parser.add_argument("--verification", default="", help="Failure verification")
    parser.add_argument("--preventive-rule", default="", help="Failure preventive rule")
    parser.add_argument("--status", default="", help="Record status")
    parser.add_argument("--lesson-type", default="operational", help="Lesson type")
    parser.add_argument("--confidence-score", type=float, default=1.0, help="Confidence score 0-1")
    
    args = parser.parse_args()
    
    writer = KnowledgeWriter()
    
    # Build kwargs for type-specific args
    extra_kwargs = {}
    if args.type == "KNOWLEDGE":
        extra_kwargs = {"category": args.category}
        if args.status:
            extra_kwargs["status"] = args.status
    elif args.type == "DECISION":
        extra_kwargs = {"decision_type": args.decision_type}
        if args.status:
            extra_kwargs["status"] = args.status
    elif args.type == "FAILURE":
        extra_kwargs = {
            "system_name": args.system_name,
            "failure_type": args.failure_type,
            "severity": args.severity,
            "fix_applied": args.fix_applied,
            "verification": args.verification,
            "preventive_rule": args.preventive_rule,
        }
        if args.status:
            extra_kwargs["status"] = args.status
    elif args.type == "LESSON":
        extra_kwargs = {
            "lesson_type": args.lesson_type,
            "confidence_score": args.confidence_score,
        }
    elif args.type == "AGENT_MEMORY":
        extra_kwargs = {
            "memory_type": args.memory_type,
            "agent_name": args.agent_name,
            "confidence_score": args.confidence_score,
        }
    
    result = writer.write(
        record_type=args.type,
        title=args.title,
        summary=args.summary,
        content=args.content,
        source=args.source,
        **extra_kwargs,
    )
    
    print(json.dumps(result, indent=2))
    
    if args.verify and result["status"] == "success":
        verify = writer.verify_record(result["record_id"], result["schema"], result["table"])
        print("\nVerification:")
        print(json.dumps(verify, indent=2, default=str))


if __name__ == "__main__":
    main()
