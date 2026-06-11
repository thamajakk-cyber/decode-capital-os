#!/usr/bin/env python3
"""
RCAF Engine — Formalized Root Cause → Corrective Fix → Acceptance → Future Prevention
=====================================================================================

Every FAIL, ERROR, BLOCKED, REGRESSION, UNHEALTHY, or CONFLICT event automatically becomes:
  Failure → Lesson → Agent Memory (constraint) → Preventive Rule → Obsidian Markdown

RCAF = Root Cause · Corrective Fix · Acceptance Verification · Future Prevention

Usage:
    # Full RCAF chain from incident
    python3 rcaf_engine.py --incident "Telegram bot double polling conflict"
    
    # With details
    python3 rcaf_engine.py --incident "Provider auth failure" \
        --system "xiaomi-provider" --severity HIGH \
        --root-cause "Gateway auth layer rejecting unauthenticated requests" \
        --fix "Added API key to gateway config" \
        --verification "E2E test returned valid response"
    
    # Dry run
    python3 rcaf_engine.py --incident "Test event" --dry-run
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from knowledge_writer import KnowledgeWriter, RecordType, REGISTRY_ROUTING


# ============================================================
# RCAF Event Schema
# ============================================================

class RCAFEvent:
    """
    Standard RCAF event schema.
    
    Compatible with:
      - failure.failure_registry
      - lesson.lesson_registry
      - agent.agent_memory_registry
    """
    
    def __init__(self, **kwargs):
        self.event_id: str = kwargs.get("event_id", f"rcaf-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
        self.timestamp: str = kwargs.get("timestamp", datetime.now(timezone.utc).isoformat())
        self.system_name: str = kwargs.get("system_name", "unknown")
        self.event_type: str = kwargs.get("event_type", "failure")
        self.severity: str = kwargs.get("severity", "MEDIUM")
        self.symptom: str = kwargs.get("symptom", "")
        self.root_cause: str = kwargs.get("root_cause", "")
        self.fix_applied: str = kwargs.get("fix_applied", "")
        self.verification: str = kwargs.get("verification", "")
        self.preventive_rule: str = kwargs.get("preventive_rule", "")
        self.lesson_summary: str = kwargs.get("lesson_summary", "")
        self.agent_memory_key: str = kwargs.get("agent_memory_key", "")
        self.evidence: dict = kwargs.get("evidence", {})
        self.status: str = kwargs.get("status", "resolved")
        self.source: str = kwargs.get("source", "rcaf-engine")
        self.agent_name: str = kwargs.get("agent_name", "Captain Mod")
        self.tags: list = kwargs.get("tags", [])
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v}
    
    def validate(self) -> list:
        """Validate event has required fields. Returns list of errors."""
        errors = []
        if not self.symptom and not self.root_cause:
            errors.append("At least one of symptom or root_cause required")
        if self.severity not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            errors.append(f"Invalid severity: {self.severity}")
        return errors


# ============================================================
# Severity Classification Engine
# ============================================================

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Severity classification rules (keyword → level, priority ordered)
SEVERITY_RULES = [
    # CRITICAL: production down, data loss, secret leak
    (SeverityLevel.CRITICAL, [
        "production down", "data loss", "secret leak", "credential leak",
        "database corrupted", "full outage", "complete failure",
        "security breach", "unauthorized access", "ransomware",
    ]),
    # HIGH: service degraded, provider broken, automation blocked
    (SeverityLevel.HIGH, [
        "service degraded", "provider broken", "automation blocked",
        "api failure", "authentication failed", "timeout",
        "container crash", "network unreachable", "dns failure",
        "ssl expired", "service unavailable", " polling conflict",
    ]),
    # MEDIUM: workflow failed but recoverable
    (SeverityLevel.MEDIUM, [
        "workflow failed", "config error", "build failed",
        "test failed", "partial failure", "recoverable",
        "retry needed", "temporary", "intermittent",
    ]),
    # LOW: minor config or documentation issue
    (SeverityLevel.LOW, [
        "documentation", "typo", "minor config", "cosmetic",
        "informational", "warning", "deprecation",
    ]),
]


def classify_severity(text: str) -> SeverityLevel:
    """Auto-classify severity from incident text."""
    text_lower = text.lower()
    for level, keywords in SEVERITY_RULES:
        for kw in keywords:
            if kw in text_lower:
                return level
    return SeverityLevel.MEDIUM  # default


def classify_failure_type(text: str) -> str:
    """Classify failure type for DB CHECK constraint."""
    text_lower = text.lower()
    mapping = [
        ("infrastructure", ["docker", "network", "server", "disk", "memory", "cpu", "container"]),
        ("integration", ["api", "webhook", "telegram", "provider", "mcp", "bridge"]),
        ("configuration", ["config", "env", "setting", "parameter", "credential"]),
        ("security", ["auth", "token", "secret", "password", "permission", "ssl"]),
        ("application", ["code", "bug", "error", "crash", "exception", "null"]),
        ("performance", ["slow", "timeout", "latency", "memory leak", "cpu spike"]),
    ]
    for ftype, keywords in mapping:
        for kw in keywords:
            if kw in text_lower:
                return ftype
    return "application"


# ============================================================
# RCAF Engine
# ============================================================

class RCAFEngine:
    """
    Formalized RCAF engine.
    
    Accepts incident → produces Failure + Lesson + Agent Memory + Preventive Rule.
    """
    
    def __init__(self, writer: KnowledgeWriter = None, dry_run: bool = False):
        self.writer = writer or KnowledgeWriter()
        self.dry_run = dry_run
    
    def process(self, event: RCAFEvent) -> dict:
        """
        Process a full RCAF chain for an incident.
        
        Returns:
            {
                "event_id": "...",
                "failure": { "status": "...", "record_id": "..." },
                "lesson": { "status": "...", "record_id": "..." },
                "agent_memory": { "status": "...", "record_id": "..." },
                "exports": [...],
                "summary": { "status": "..." }
            }
        """
        # Validate
        errors = event.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}
        
        # Auto-classify severity if needed
        if event.severity == "MEDIUM" and event.symptom:
            classified = classify_severity(event.symptom)
            event.severity = classified.value.upper()
        
        # Auto-classify failure type
        failure_type = classify_failure_type(f"{event.symptom} {event.root_cause}")
        
        result = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "system_name": event.system_name,
            "severity": event.severity,
            "failure_type": failure_type,
        }
        
        # ── Step 1: Write Failure Registry ──
        failure_result = self._write_failure(event, failure_type)
        result["failure"] = failure_result
        
        failure_id = failure_result.get("record_id") if failure_result.get("status") == "success" else None
        
        # ── Step 2: Write Lesson Registry (linked to failure) ──
        lesson_result = self._write_lesson(event, failure_id)
        result["lesson"] = lesson_result
        
        lesson_id = lesson_result.get("record_id") if lesson_result.get("status") == "success" else None
        
        # ── Step 3: Write Agent Memory (preventive rule as constraint) ──
        memory_result = self._write_agent_memory(event)
        result["agent_memory"] = memory_result
        
        # ── Step 4: Export to Obsidian ──
        exports = []
        if not self.dry_run:
            exports = self._export_all()
        result["exports"] = exports
        
        # ── Summary ──
        steps = [failure_result, lesson_result, memory_result]
        successes = sum(1 for s in steps if s.get("status") == "success")
        result["summary"] = {
            "total_steps": 3,
            "successes": successes,
            "failures": 3 - successes,
            "status": "PASS" if successes == 3 else "PARTIAL" if successes > 0 else "FAIL",
            "failure_id": failure_id,
            "lesson_id": lesson_id,
            "memory_id": memory_result.get("record_id"),
        }
        
        return result
    
    def _write_failure(self, event: RCAFEvent, failure_type: str) -> dict:
        """Write to failure.failure_registry."""
        if self.dry_run:
            return {"status": "dry_run", "record_type": "failure"}
        
        title = f"{event.system_name}: {event.symptom[:80]}" if event.symptom else f"{event.system_name} incident"
        
        return self.writer.write(
            record_type="failure",
            title=title,
            summary=event.symptom[:500] if event.symptom else event.root_cause[:500],
            content=event.root_cause or event.symptom,
            tags=event.tags,
            source=event.source,
            system_name=event.system_name,
            failure_type=failure_type,
            severity=event.severity.lower(),
            fix_applied=event.fix_applied,
            verification=event.verification,
            preventive_rule=event.preventive_rule,
            status=event.status,
        )
    
    def _write_lesson(self, event: RCAFEvent, failure_id: Optional[str]) -> dict:
        """Write to lesson.lesson_registry, linked to failure."""
        if self.dry_run:
            return {"status": "dry_run", "record_type": "lesson"}
        
        title = event.lesson_summary or f"Prevention: {event.system_name} - {event.symptom[:60]}"
        
        lesson_content = {
            "root_cause": event.root_cause,
            "fix_applied": event.fix_applied,
            "verification": event.verification,
            "preventive_rule": event.preventive_rule,
        }
        
        return self.writer.write(
            record_type="lesson",
            title=title,
            summary=event.preventive_rule or event.lesson_summary or event.symptom[:500],
            content=lesson_content,
            tags=event.tags,
            source=event.source,
            lesson_type="operational",
            related_failure_id=failure_id,
            confidence_score=1.0,
        )
    
    def _write_agent_memory(self, event: RCAFEvent) -> dict:
        """Write to agent.agent_memory_registry as preventive constraint."""
        if self.dry_run:
            return {"status": "dry_run", "record_type": "agent_memory"}
        
        memory_key = event.agent_memory_key or f"prevent-{event.system_name}"
        memory_value = {
            "preventive_rule": event.preventive_rule,
            "root_cause_summary": event.root_cause[:200] if event.root_cause else event.symptom[:200],
            "fix_summary": event.fix_applied[:200] if event.fix_applied else "N/A",
        }
        
        return self.writer.write(
            record_type="agent_memory",
            title=memory_key,
            summary=event.preventive_rule or f"Prevention rule for {event.system_name}",
            content=memory_value,
            tags=event.tags + ["preventive-rule", "rcaf"],
            source=event.source,
            agent_name=event.agent_name,
            memory_type="constraint",
            confidence_score=1.0,
        )
    
    def _export_all(self) -> list:
        """Run Obsidian exporter for all schemas."""
        exports = []
        try:
            import subprocess
            export_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export_to_obsidian.py")
            result = subprocess.run(
                ["python3", export_script, "--mode", "incremental"],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "POSTGRES_HOST": "127.0.0.1"}
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "Total:" in line:
                        exports.append({"status": "success", "details": line.strip()})
                        break
            else:
                exports.append({"status": "error", "details": result.stderr[:200]})
        except Exception as e:
            exports.append({"status": "error", "details": str(e)[:200]})
        return exports


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="RCAF Engine — Formalized Incident Processing")
    parser.add_argument("--incident", required=True, help="Incident description")
    parser.add_argument("--system", default="unknown", help="Affected system")
    parser.add_argument("--severity", default="MEDIUM", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                       help="Severity level")
    parser.add_argument("--root-cause", default="", help="Root cause analysis")
    parser.add_argument("--fix", default="", help="Corrective fix applied")
    parser.add_argument("--verification", default="", help="Acceptance verification")
    parser.add_argument("--preventive-rule", default="", help="Future prevention rule")
    parser.add_argument("--lesson-summary", default="", help="Lesson summary")
    parser.add_argument("--memory-key", default="", help="Agent memory key")
    parser.add_argument("--agent-name", default="Captain Mod", help="Agent name")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--source", default="rcaf-engine", help="Event source")
    
    args = parser.parse_args()
    
    event = RCAFEvent(
        system_name=args.system,
        severity=args.severity,
        symptom=args.incident,
        root_cause=args.root_cause,
        fix_applied=args.fix,
        verification=args.verification,
        preventive_rule=args.preventive_rule,
        lesson_summary=args.lesson_summary,
        agent_memory_key=args.memory_key,
        agent_name=args.agent_name,
        source=args.source,
    )
    
    engine = RCAFEngine(dry_run=args.dry_run)
    result = engine.process(event)
    
    print(json.dumps(result, indent=2, default=str))
    
    # Exit code
    status = result.get("summary", {}).get("status", result.get("status", "FAIL"))
    sys.exit(0 if status in ["PASS", "dry_run"] else 1)


if __name__ == "__main__":
    main()
