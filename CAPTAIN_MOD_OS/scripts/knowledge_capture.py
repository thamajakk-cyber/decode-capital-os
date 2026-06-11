#!/usr/bin/env python3
"""
Knowledge Capture Automation Engine
====================================
Automatically transforms operational events into persistent Knowledge OS records.

Event → Classification → Database Write → Obsidian Export

Usage:
    # Direct event capture
    python3 knowledge_capture.py --event "PostgreSQL container health check failed"
    
    # Capture with explicit type
    python3 knowledge_capture.py --event "SSL certificate renewal" --type DECISION
    
    # Capture failure with details
    python3 knowledge_capture.py --event "Telegram bot timeout" --type FAILURE \
        --system "telegram-bot" --severity "high"
    
    # RCAF chain from a failure description
    python3 knowledge_capture.py --rcaf --event "Docker network isolation" \
        --system "knowledge-os-postgres" --severity "high"
    
    # Dry run (no DB writes)
    python3 knowledge_capture.py --event "Test event" --dry-run
    
    # From stdin (pipeline)
    echo "Deployment succeeded" | python3 knowledge_capture.py --stdin
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone

# Import the knowledge writer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from knowledge_writer import KnowledgeWriter, RecordType, classify_record, REGISTRY_ROUTING


# ============================================================
# Event Types
# ============================================================

class EventType:
    AUDIT = "audit"
    VERIFICATION = "verification"
    DEPLOYMENT = "deployment"
    FAILURE = "failure"
    LESSON = "lesson"
    DECISION = "decision"
    SYSTEM = "system"
    UNKNOWN = "unknown"


# ============================================================
# Event Capture Engine
# ============================================================

class EventCapture:
    """Captures and processes operational events."""
    
    def __init__(self, writer: KnowledgeWriter, dry_run: bool = False):
        self.writer = writer
        self.dry_run = dry_run
        self.captured_events = []
    
    def capture(self, event_text: str, event_type: str = None,
                system: str = "", severity: str = "medium",
                source: str = "auto-capture", **kwargs) -> dict:
        """
        Capture an event, classify it, and write to Knowledge OS.
        
        Returns dict with:
            - event_id: unique identifier
            - classification: detected record type
            - writes: list of database writes performed
            - exports: list of markdown files generated
        """
        event_id = f"event-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        # Step 1: Classify
        if event_type:
            try:
                record_type = RecordType(event_type.lower())
            except ValueError:
                record_type = classify_record(event_text)
        else:
            record_type = classify_record(event_text)
        
        schema, table = REGISTRY_ROUTING[record_type]
        
        # Step 2: Build write parameters
        write_params = self._build_params(record_type, event_text, system, severity, **kwargs)
        
        # Step 3: Write to database
        write_result = None
        if not self.dry_run:
            write_result = self.writer.write(
                record_type=record_type.value,
                title=write_params["title"],
                summary=write_params["summary"],
                content=write_params["content"],
                tags=write_params.get("tags", []),
                source=source,
                **write_params.get("extra", {})
            )
        else:
            write_result = {
                "status": "dry_run",
                "record_type": record_type.value,
                "schema": schema,
                "table": table,
                "title": write_params["title"],
            }
        
        # Step 4: Export to Obsidian (if write succeeded)
        export_result = None
        if write_result.get("status") == "success" and not self.dry_run:
            export_result = self._export_to_obsidian(schema, table)
        
        result = {
            "event_id": event_id,
            "event_text": event_text[:200],
            "classification": record_type.value,
            "schema": schema,
            "table": table,
            "write": write_result,
            "export": export_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        self.captured_events.append(result)
        return result
    
    def capture_rcaf_chain(self, event_text: str, system: str = "",
                           severity: str = "high", source: str = "auto-capture",
                           **kwargs) -> dict:
        """
        Generate a full RCAF chain from a failure event:
        1. Failure Registry entry
        2. Lesson Registry entry (linked to failure)
        3. Agent Memory entry (constraint/lesson)
        
        Returns dict with all chain results.
        """
        chain = {
            "chain_type": "rcaf",
            "trigger": event_text[:200],
            "steps": [],
        }
        
        # Step 1: Write Failure
        failure_result = self.writer.write(
            record_type="failure",
            title=kwargs.get("title", self._generate_title(event_text)),
            summary=event_text[:500],
            content=event_text,
            tags=kwargs.get("tags", []),
            source=source,
            system_name=system or "unknown",
            failure_type=kwargs.get("failure_type", "application"),
            severity=severity,
            fix_applied=kwargs.get("fix_applied", ""),
            verification=kwargs.get("verification", ""),
            preventive_rule=kwargs.get("preventive_rule", ""),
            status="resolved" if kwargs.get("fix_applied") else "open",
        )
        chain["steps"].append({"step": "failure", "result": failure_result})
        
        failure_id = None
        if failure_result.get("status") == "success":
            failure_id = failure_result["record_id"]
        
        # Step 2: Write Lesson (linked to failure)
        lesson_result = self.writer.write(
            record_type="lesson",
            title=kwargs.get("lesson_title", f"Lesson: {self._generate_title(event_text)}"),
            summary=kwargs.get("lesson_summary", f"Prevention for: {event_text[:200]}"),
            content=kwargs.get("lesson_content", {
                "root_cause": event_text,
                "prevention": kwargs.get("preventive_rule", "Verify before deploy"),
                "rule": kwargs.get("lesson_rule", "Always verify configuration"),
            }),
            tags=kwargs.get("tags", []),
            source=source,
            lesson_type=kwargs.get("lesson_type", "operational"),
            related_failure_id=failure_id,
            confidence_score=kwargs.get("confidence_score", 1.0),
        )
        chain["steps"].append({"step": "lesson", "result": lesson_result})
        
        # Step 3: Write Agent Memory
        memory_result = self.writer.write(
            record_type="agent_memory",
            title=kwargs.get("memory_key", f"lesson-{self._slugify(self._generate_title(event_text))}"),
            summary=event_text[:500],
            content=kwargs.get("memory_value", f"Lesson learned from: {event_text}. Prevention: {kwargs.get('preventive_rule', 'N/A')}"),
            tags=kwargs.get("tags", []),
            source=source,
            agent_name=kwargs.get("agent_name", "Captain Mod"),
            memory_type=kwargs.get("memory_type", "constraint"),
            confidence_score=kwargs.get("confidence_score", 1.0),
        )
        chain["steps"].append({"step": "agent_memory", "result": memory_result})
        
        # Export all
        exports = []
        if not self.dry_run:
            for schema_name in ["failure", "lesson", "agent"]:
                table_name = REGISTRY_ROUTING[RecordType(schema_name if schema_name != "agent" else "agent_memory")][1]
                exp = self._export_to_obsidian(schema_name, table_name)
                if exp:
                    exports.append(exp)
        
        chain["exports"] = exports
        chain["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Summary
        successes = sum(1 for s in chain["steps"] if s["result"].get("status") == "success")
        chain["summary"] = {
            "total_steps": len(chain["steps"]),
            "successes": successes,
            "failures": len(chain["steps"]) - successes,
            "status": "success" if successes == len(chain["steps"]) else "partial",
        }
        
        return chain
    
    def _build_params(self, record_type: RecordType, event_text: str,
                      system: str, severity: str, **kwargs) -> dict:
        """Build write parameters based on record type."""
        title = kwargs.get("title", self._generate_title(event_text))
        summary = event_text[:500]
        
        params = {
            "title": title,
            "summary": summary,
            "content": event_text,
            "tags": kwargs.get("tags", []),
        }
        
        if record_type == RecordType.KNOWLEDGE:
            params["extra"] = {"category": kwargs.get("category", "operational")}
        
        elif record_type == RecordType.DECISION:
            params["extra"] = {
                "decision_type": kwargs.get("decision_type", "technical"),
                "status": kwargs.get("status", "executed"),
                "chosen_option": kwargs.get("chosen_option", ""),
            }
        
        elif record_type == RecordType.FAILURE:
            params["extra"] = {
                "system_name": system or "unknown",
                "failure_type": kwargs.get("failure_type", "application"),
                "severity": severity,
                "fix_applied": kwargs.get("fix_applied", ""),
                "verification": kwargs.get("verification", ""),
                "preventive_rule": kwargs.get("preventive_rule", ""),
                "status": kwargs.get("status", "resolved"),
            }
        
        elif record_type == RecordType.LESSON:
            params["extra"] = {
                "lesson_type": kwargs.get("lesson_type", "operational"),
                "confidence_score": kwargs.get("confidence_score", 1.0),
            }
        
        elif record_type == RecordType.AGENT_MEMORY:
            params["extra"] = {
                "agent_name": kwargs.get("agent_name", "Captain Mod"),
                "memory_type": kwargs.get("memory_type", "observation"),
                "confidence_score": kwargs.get("confidence_score", 1.0),
            }
        
        return params
    
    def _export_to_obsidian(self, schema: str, table: str) -> dict:
        """Run the Obsidian exporter and return result."""
        try:
            import subprocess
            export_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export_to_obsidian.py")
            result = subprocess.run(
                ["python3", export_script, "--mode", "incremental"],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "POSTGRES_HOST": "127.0.0.1"}
            )
            if result.returncode == 0:
                # Parse the total from output
                for line in result.stdout.split("\n"):
                    if "Total:" in line:
                        return {"status": "success", "details": line.strip()}
                return {"status": "success", "details": "Export completed"}
            return {"status": "error", "details": result.stderr[:200]}
        except Exception as e:
            return {"status": "error", "details": str(e)[:200]}
    
    def _generate_title(self, event_text: str) -> str:
        """Generate a title from event text."""
        # Take first sentence, clean up
        title = event_text.split(".")[0].split("\n")[0]
        title = title[:100].strip()
        if not title:
            title = f"Event {datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        return title
    
    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug[:60].strip("-")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Knowledge Capture Automation Engine")
    parser.add_argument("--event", required=True, help="Event text to capture")
    parser.add_argument("--type", choices=["KNOWLEDGE", "DECISION", "FAILURE", "LESSON", "AGENT_MEMORY"],
                       help="Force classification (auto-detect if omitted)")
    parser.add_argument("--system", default="", help="Affected system name")
    parser.add_argument("--severity", default="medium", help="Severity (low|medium|high|critical)")
    parser.add_argument("--source", default="auto-capture", help="Event source")
    parser.add_argument("--rcaf", action="store_true", help="Generate full RCAF chain (failure → lesson → memory)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--stdin", action="store_true", help="Read event from stdin")
    parser.add_argument("--title", default="", help="Override title")
    parser.add_argument("--fix-applied", default="", help="Fix applied (for failures)")
    parser.add_argument("--preventive-rule", default="", help="Preventive rule (for lessons)")
    parser.add_argument("--agent-name", default="Captain Mod", help="Agent name (for memory)")
    
    args = parser.parse_args()
    
    # Read event text
    if args.stdin:
        event_text = sys.stdin.read().strip()
    else:
        event_text = args.event
    
    writer = KnowledgeWriter()
    capture = EventCapture(writer, dry_run=args.dry_run)
    
    if args.rcaf:
        # RCAF chain mode
        result = capture.capture_rcaf_chain(
            event_text=event_text,
            system=args.system,
            severity=args.severity,
            source=args.source,
            title=args.title,
            fix_applied=args.fix_applied,
            preventive_rule=args.preventive_rule,
            agent_name=args.agent_name,
        )
    else:
        # Single event capture
        result = capture.capture(
            event_text=event_text,
            event_type=args.type,
            system=args.system,
            severity=args.severity,
            source=args.source,
            title=args.title,
            fix_applied=args.fix_applied,
            preventive_rule=args.preventive_rule,
            agent_name=args.agent_name,
        )
    
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
