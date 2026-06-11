#!/usr/bin/env python3
"""
Knowledge Curation Engine
==========================
Transforms Knowledge OS from collection system to intelligence repository.

Detects: Duplicates, Overlaps, Contradictions, Weak Records, Fragmented Chains
Actions: Merge, Consolidate, Promote, Archive

Usage:
    python3 knowledge_curation.py --audit
    python3 knowledge_curation.py --detect-duplicates
    python3 knowledge_curation.py --detect-contradictions
    python3 knowledge_curation.py --generate-assets
    python3 knowledge_curation.py --promote
    python3 knowledge_curation.py --archive
    python3 knowledge_curation.py --full-curation
    python3 knowledge_curation.py --dashboard
"""

import os, sys, json, re, argparse
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed")
    sys.exit(1)

DB = {
    "host": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
    "port": int(os.environ.get("POSTGRES_PORT", "5432")),
    "dbname": os.environ.get("POSTGRES_DB", "knowledge_os"),
    "user": os.environ.get("POSTGRES_USER", "knowledge_admin"),
    "password": os.environ.get("POSTGRES_PASSWORD", ""),
}

TABLES = {
    "knowledge": "knowledge_registry",
    "decision": "decision_registry",
    "failure": "failure_registry",
    "lesson": "lesson_registry",
    "agent": "agent_memory_registry",
}


def connect():
    return psycopg2.connect(**DB)


def normalize(text):
    """Normalize text for comparison."""
    if not text:
        return ""
    t = str(text).lower().strip()
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t


def similarity(a, b):
    """Simple word-overlap similarity."""
    wa = set(normalize(a).split())
    wb = set(normalize(b).split())
    if not wa or not wb:
        return 0
    return len(wa & wb) / max(len(wa), len(wb))


class CurationEngine:
    def __init__(self):
        self.conn = connect()
        self.stats = {}

    def close(self):
        if self.conn:
            self.conn.close()

    def _all_records(self):
        """Fetch all records across all registries."""
        records = []
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        for schema, table in TABLES.items():
            cur.execute(f"SELECT *, '{schema}' as _schema FROM {schema}.{table}")
            for row in cur.fetchall():
                d = dict(row)
                d["_schema"] = schema
                # Build a searchable text
                title = d.get("title", d.get("system_name", d.get("memory_key", "")))
                summary = d.get("summary", d.get("symptom", d.get("memory_value", "")))
                if isinstance(summary, dict):
                    summary = json.dumps(summary, default=str)
                d["_title"] = str(title or "")
                d["_text"] = normalize(f"{title} {summary}")
                records.append(d)
        return records

    # ── Phase 2: Duplicate Detection ──

    def detect_duplicates(self):
        records = self._all_records()
        clusters = []
        used = set()

        for i, r1 in enumerate(records):
            if i in used:
                continue
            cluster = [r1]
            for j, r2 in enumerate(records):
                if j <= i or j in used:
                    continue
                # Same schema, high text similarity
                sim = similarity(r1["_text"], r2["_text"])
                if sim > 0.45:
                    cluster.append(r2)
                    used.add(j)
            if len(cluster) > 1:
                used.add(i)
                # Pick canonical (highest quality)
                canonical = max(cluster, key=lambda x: float(x.get("quality_score", 0) or 0))
                clusters.append({
                    "canonical": canonical,
                    "duplicates": [c for c in cluster if c["id"] != canonical["id"]],
                    "similarity": round(max(similarity(r1["_text"], c["_text"]) for c in cluster[1:]), 2) if len(cluster) > 1 else 0,
                    "count": len(cluster),
                })

        self.stats["duplicates_found"] = len(clusters)
        self.stats["duplicate_records"] = sum(c["count"] for c in clusters)
        return clusters

    # ── Phase 3: Contradiction Detection ──

    def detect_contradictions(self):
        records = self._all_records()
        contradictions = []

        # Check agent memories for conflicting constraints
        constraints = [r for r in records if r.get("memory_type") == "constraint"]
        for i, c1 in enumerate(constraints):
            for j, c2 in enumerate(constraints):
                if j <= i:
                    continue
                t1 = str(c1.get("memory_value", ""))
                t2 = str(c2.get("memory_value", ""))
                # Look for negation patterns
                neg_patterns = ["never", "always", "must not", "must", "do not", "should not"]
                for neg in neg_patterns:
                    if neg in normalize(t1) and any(
                        n in normalize(t2) and n != neg
                        for n in neg_patterns if n in normalize(t2)
                    ):
                        if similarity(t1, t2) > 0.3:
                            contradictions.append({
                                "type": "agent_constraint_conflict",
                                "record_a": {"schema": "agent", "id": str(c1["id"]), "key": c1.get("memory_key", "")},
                                "record_b": {"schema": "agent", "id": str(c2["id"]), "key": c2.get("memory_key", "")},
                                "severity": "MEDIUM",
                                "description": f"Potential constraint conflict between {c1.get('memory_key', '')} and {c2.get('memory_key', '')}",
                            })

        # Check lessons for conflicting rules
        lessons = [r for r in records if r["_schema"] == "lesson"]
        for i, l1 in enumerate(lessons):
            for j, l2 in enumerate(lessons):
                if j <= i:
                    continue
                if similarity(l1["_text"], l2["_text"]) > 0.6 and l1["id"] != l2["id"]:
                    contradictions.append({
                        "type": "duplicate_lesson",
                        "record_a": {"schema": "lesson", "id": str(l1["id"]), "title": l1.get("title", "")},
                        "record_b": {"schema": "lesson", "id": str(l2["id"]), "title": l2.get("title", "")},
                        "severity": "LOW",
                        "description": f"Duplicate lessons: {l1.get('title', '')} ≈ {l2.get('title', '')}",
                    })

        self.stats["contradictions_found"] = len(contradictions)
        return contradictions

    # ── Phase 4: Knowledge Asset Generation ──

    def generate_assets(self):
        records = self._all_records()
        assets = []

        # Group by failure → lesson → rule chains
        failures = [r for r in records if r["_schema"] == "failure"]
        lessons = [r for r in records if r["_schema"] == "lesson"]
        rules = [r for r in records if r.get("memory_type") == "constraint"]

        # Build asset from duplicate clusters
        clusters = self.detect_duplicates()

        for cluster in clusters:
            canonical = cluster["canonical"]
            schema = canonical["_schema"]

            # Find related records
            related_failures = [r for r in failures if similarity(r["_text"], canonical["_text"]) > 0.3]
            related_lessons = [r for r in lessons if similarity(r["_text"], canonical["_text"]) > 0.3]
            related_rules = [r for r in rules if similarity(r["_text"], canonical["_text"]) > 0.3]

            asset = {
                "asset_name": canonical.get("title", canonical.get("system_name", canonical.get("memory_key", "Unknown"))),
                "category": schema,
                "source_records": [{"schema": c["_schema"], "id": str(c["id"]), "title": c.get("title", c.get("system_name", c.get("memory_key", "")))} for c in [canonical] + cluster["duplicates"]],
                "root_cause": related_failures[0].get("root_cause", "") if related_failures else "",
                "lesson": related_lessons[0].get("summary", "") if related_lessons else "",
                "preventive_rule": next((r.get("memory_value", {}).get("preventive_rule", "") if isinstance(r.get("memory_value"), dict) else "" for r in related_rules if r.get("memory_value")), ""),
                "quality_score": float(canonical.get("quality_score", 0) or 0),
                "confidence_score": float(canonical.get("confidence_score", 0) or 0),
                "asset_type": "knowledge_asset",
            }
            assets.append(asset)

        # Build standalone assets from high-quality records
        standalone = [r for r in records if float(r.get("quality_score", 0) or 0) >= 55
                      and not any(r["id"] == c["canonical"]["id"] for c in clusters)]
        for r in standalone[:10]:
            asset = {
                "asset_name": r.get("title", r.get("system_name", r.get("memory_key", "Unknown"))),
                "category": r["_schema"],
                "source_records": [{"schema": r["_schema"], "id": str(r["id"]), "title": r.get("title", "")}],
                "quality_score": float(r.get("quality_score", 0) or 0),
                "confidence_score": float(r.get("confidence_score", 0) or 0),
                "asset_type": "knowledge_asset",
            }
            assets.append(asset)

        # Store in curated_assets
        cur = self.conn.cursor()
        for asset in assets:
            cur.execute("""
                INSERT INTO knowledge.curated_assets
                (asset_name, category, source_records, root_cause, lesson,
                 preventive_rule, quality_score, confidence_score, asset_type)
                VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                asset["asset_name"], asset["category"],
                json.dumps(asset.get("source_records", []), default=str),
                asset.get("root_cause", ""), asset.get("lesson", ""),
                asset.get("preventive_rule", ""),
                asset["quality_score"], asset["confidence_score"],
                asset["asset_type"],
            ))
        self.conn.commit()

        self.stats["assets_generated"] = len(assets)
        return assets

    # ── Phase 5: Promotion Engine ──

    def promote_records(self):
        records = self._all_records()
        promoted = []

        for r in records:
            score = float(r.get("quality_score", 0) or 0)
            if score >= 90:
                asset_type = "organizational_principle"
            elif score >= 80:
                asset_type = "verified_knowledge"
            else:
                continue

            title = r.get("title", r.get("system_name", r.get("memory_key", "Unknown")))
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO knowledge.curated_assets
                (asset_name, category, source_records, quality_score, confidence_score, asset_type)
                VALUES (%s, %s, %s::jsonb, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                title, r["_schema"],
                json.dumps([{"schema": r["_schema"], "id": str(r["id"])}]),
                score, float(r.get("confidence_score", 0) or 0), asset_type,
            ))
            promoted.append({"title": title, "type": asset_type, "score": score})

        self.conn.commit()
        self.stats["promoted"] = len(promoted)
        return promoted

    # ── Phase 6: Archive Engine ──

    def archive_weak(self):
        records = self._all_records()
        clusters = self.detect_duplicates()
        duplicate_ids = set()
        for c in clusters:
            for d in c["duplicates"]:
                duplicate_ids.add(str(d["id"]))

        archived = []
        for r in records:
            score = float(r.get("quality_score", 0) or 0)
            rid = str(r["id"])
            if score < 30 and rid in duplicate_ids:
                # Mark as archived (update status)
                schema = r["_schema"]
                table = TABLES[schema]
                cur = self.conn.cursor()
                if schema == "agent":
                    cur.execute(f"UPDATE {schema}.{table} SET memory_type = 'workflow' WHERE id = %s AND memory_type = 'constraint'", (rid,))
                else:
                    try:
                        cur.execute(f"UPDATE {schema}.{table} SET status = 'archived' WHERE id = %s", (rid,))
                    except Exception:
                        pass  # table may not have status column
                archived.append({"id": rid, "schema": schema, "score": score})

        self.conn.commit()
        self.stats["archived"] = len(archived)
        return archived

    # ── Dashboard Queries ──

    def dashboard(self):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Top knowledge assets
        cur.execute("SELECT asset_name, category, quality_score, asset_type FROM knowledge.curated_assets ORDER BY quality_score DESC LIMIT 10")
        top_assets = [dict(r) for r in cur.fetchall()]

        # Quality trend
        cur.execute("""
            SELECT 'knowledge' as s, round(avg(quality_score),1) as avg FROM knowledge.knowledge_registry
            UNION ALL SELECT 'failure', round(avg(quality_score),1) FROM failure.failure_registry
            UNION ALL SELECT 'lesson', round(avg(quality_score),1) FROM lesson.lesson_registry
            UNION ALL SELECT 'agent', round(avg(quality_score),1) FROM agent.agent_memory_registry
            ORDER BY avg DESC
        """)
        quality_trend = [dict(r) for r in cur.fetchall()]

        # Duplicate clusters
        clusters = self.detect_duplicates()

        # Overall stats
        cur.execute("""
            SELECT count(*) as total, round(avg(quality_score),1) as avg,
                   sum(CASE WHEN quality_grade IN ('A+','A','B') THEN 1 ELSE 0 END) as ab,
                   sum(CASE WHEN quality_grade = 'C' THEN 1 ELSE 0 END) as c_grade,
                   sum(CASE WHEN quality_grade = 'D' THEN 1 ELSE 0 END) as d_grade,
                   sum(CASE WHEN quality_grade = 'F' THEN 1 ELSE 0 END) as f_grade
            FROM (
              SELECT quality_score, quality_grade FROM knowledge.knowledge_registry
              UNION ALL SELECT quality_score, quality_grade FROM decision.decision_registry
              UNION ALL SELECT quality_score, quality_grade FROM failure.failure_registry
              UNION ALL SELECT quality_score, quality_grade FROM lesson.lesson_registry
              UNION ALL SELECT quality_score, quality_grade FROM agent.agent_memory_registry
            ) all_r
        """)
        overall = dict(cur.fetchone())

        return {
            "overall": overall,
            "top_assets": top_assets,
            "quality_by_category": quality_trend,
            "duplicate_clusters": len(clusters),
            "duplicate_records": sum(c["count"] for c in clusters),
        }


def main():
    parser = argparse.ArgumentParser(description="Knowledge Curation Engine")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--detect-duplicates", action="store_true")
    parser.add_argument("--detect-contradictions", action="store_true")
    parser.add_argument("--generate-assets", action="store_true")
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--archive", action="store_true")
    parser.add_argument("--full-curation", action="store_true")
    parser.add_argument("--dashboard", action="store_true")
    args = parser.parse_args()

    engine = CurationEngine()
    try:
        if args.audit:
            records = engine._all_records()
            print(json.dumps({"total": len(records), "by_schema": {s: sum(1 for r in records if r["_schema"] == s) for s in TABLES}}, indent=2))

        elif args.detect_duplicates:
            clusters = engine.detect_duplicates()
            print(json.dumps({"clusters": len(clusters), "total_duplicates": engine.stats.get("duplicate_records", 0),
                             "details": [{"canonical": c["canonical"].get("title", c["canonical"].get("memory_key", "")),
                                          "count": c["count"], "similarity": c["similarity"]} for c in clusters]}, indent=2, default=str))

        elif args.detect_contradictions:
            contradictions = engine.detect_contradictions()
            print(json.dumps({"total": len(contradictions), "details": contradictions}, indent=2, default=str))

        elif args.generate_assets:
            assets = engine.generate_assets()
            print(json.dumps({"total": len(assets), "stats": engine.stats}, indent=2, default=str))

        elif args.promote:
            promoted = engine.promote_records()
            print(json.dumps({"promoted": len(promoted), "details": promoted}, indent=2, default=str))

        elif args.archive:
            archived = engine.archive_weak()
            print(json.dumps({"archived": len(archived), "stats": engine.stats}, indent=2, default=str))

        elif args.full_curation:
            print("=== FULL CURATION ===")
            print("\n--- Duplicates ---")
            clusters = engine.detect_duplicates()
            print(f"  Clusters: {len(clusters)}, Duplicate records: {engine.stats.get('duplicate_records', 0)}")
            for c in clusters:
                print(f"    [{c['count']}x] {c['canonical'].get('title', c['canonical'].get('memory_key', 'N/A'))[:60]} (sim={c['similarity']})")

            print("\n--- Contradictions ---")
            contradictions = engine.detect_contradictions()
            print(f"  Found: {len(contradictions)}")

            print("\n--- Assets ---")
            assets = engine.generate_assets()
            print(f"  Generated: {len(assets)}")

            print("\n--- Promotion ---")
            promoted = engine.promote_records()
            print(f"  Promoted: {len(promoted)}")

            print("\n--- Archive ---")
            archived = engine.archive_weak()
            print(f"  Archived: {len(archived)}")

            print(f"\n=== STATS: {json.dumps(engine.stats)} ===")

        elif args.dashboard:
            dash = engine.dashboard()
            print(json.dumps(dash, indent=2, default=str))

        else:
            parser.print_help()
    finally:
        engine.close()


if __name__ == "__main__":
    main()
