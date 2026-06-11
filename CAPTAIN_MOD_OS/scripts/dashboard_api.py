#!/usr/bin/env python3
"""
Founder Dashboard API
======================
Read-only dashboard engine for Captain Mod OS.

Endpoints (via --flag):
  --health         System health check
  --executive      Executive overview metrics
  --knowledge      Knowledge intelligence metrics
  --governance     Governance center metrics
  --rcaf           RCAF activity metrics
  --founder        Founder intelligence (top records)
  --top-assets     Top knowledge assets
  --metrics        All metrics
  --refresh        Refresh materialized views + calculate scores
  --populate       Generate all dashboard metrics

Usage:
    python3 dashboard_api.py --refresh
    python3 dashboard_api.py --executive
    python3 dashboard_api.py --populate
"""

import os, sys, json, argparse
from decimal import Decimal
from datetime import datetime, date
from datetime import datetime, timezone

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




class SafeEncoder(json.JSONEncoder):
    def default(self, o):
        from decimal import Decimal
        from datetime import datetime, date
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return super().default(o)

def safe_json(obj):
    return json.dumps(obj, indent=2, cls=SafeEncoder)

def connect():
    return psycopg2.connect(**DB)


def grade(score):
    if score >= 95: return "A+"
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


class DashboardAPI:
    def __init__(self):
        self.conn = connect()

    def close(self):
        if self.conn:
            self.conn.close()

    def _q(self, sql, params=None):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        return cur.fetchall()

    # ── Refresh Materialized Views ──

    def refresh(self):
        views = [
            "dashboard.mv_executive_metrics",
            "dashboard.mv_knowledge_metrics",
            "dashboard.mv_governance_metrics",
            "dashboard.mv_rcaf_metrics",
            "dashboard.mv_founder_intelligence",
        ]
        for v in views:
            self.conn.cursor().execute(f"REFRESH MATERIALIZED VIEW {v}")
        self.conn.commit()
        return {"status": "refreshed", "views": len(views)}

    # ── KPI Calculations ──

    def _calc_knowledge_health(self):
        """Knowledge Health Score (0-100)"""
        rows = self._q("SELECT * FROM dashboard.mv_executive_metrics")
        if not rows:
            return 0
        r = rows[0]
        avg_q = float(r["avg_quality"] or 0)
        total = int(r["total_records"] or 0)
        assets = int(r["curated_assets"] or 0)
        resolved = int(r["resolved_contradictions"] or 0)
        open_c = int(r["open_contradictions"] or 0)

        # Components (each 0-20, total 0-100)
        quality = min(20, avg_q / 5)  # 0-100 → 0-20
        coverage = min(20, (assets / max(total, 1)) * 100)  # asset coverage
        dedup = max(0, 20 - open_c * 4)  # penalty for open contradictions
        governance = min(20, resolved * 4)  # resolved contradictions
        completeness = min(20, 10 if total > 50 else total / 3)

        return round(quality + coverage + dedup + governance + completeness, 1)

    def _calc_governance_score(self):
        """Governance Score (0-100)"""
        rows = self._q("SELECT * FROM dashboard.mv_governance_metrics")
        if not rows:
            return 0
        r = rows[0]
        principles = int(r["principles_count"] or 0)
        policies = int(r["policies_count"] or 0)
        rules = int(r["rules_count"] or 0)
        sops = int(r["sops_count"] or 0)
        resolved = int(r["resolved_conflicts"] or 0)
        open_c = int(r["open_conflicts"] or 0)

        # Each category max 20
        p_score = min(20, principles * 1.5)  # 13 → 19.5
        pol_score = min(20, policies * 3)    # 7 → 20
        r_score = min(20, rules * 1.7)       # 12 → 20
        s_score = min(20, sops * 1.3)        # 15 → 19.5
        c_score = min(20, resolved * 4 - open_c * 2)  # 5 resolved → 20

        return round(max(0, p_score + pol_score + r_score + s_score + c_score), 1)

    def _calc_automation_score(self):
        """Automation Score (0-100)"""
        rows = self._q("""
            SELECT
              (SELECT count(*) FROM agent.agent_memory_registry WHERE memory_type='constraint') as rules,
              (SELECT count(*) FROM knowledge.curated_assets) as assets,
              (SELECT count(*) FROM governance.sop_library WHERE status='active') as sops,
              (SELECT count(*) FROM failure.failure_registry WHERE status='resolved') as resolved,
              (SELECT count(*) FROM failure.failure_registry) as total_failures
        """)
        if not rows:
            return 0
        r = rows[0]
        rules = int(r["rules"] or 0)
        assets = int(r["assets"] or 0)
        sops = int(r["sops"] or 0)
        resolved = int(r["resolved"] or 0)
        total = int(r["total_failures"] or 1)

        # Components
        capture = min(25, rules * 0.5)  # rules as proxy for capture
        enrich = min(25, assets * 0.8)
        govern = min(25, sops * 1.7)
        resolution = min(25, (resolved / total) * 25)

        return round(capture + enrich + govern + resolution, 1)

    # ── Endpoints ──

    def health(self):
        k_h = self._calc_knowledge_health()
        g_s = self._calc_governance_score()
        a_s = self._calc_automation_score()
        overall = round((k_h + g_s + a_s) / 3, 1)
        g = grade(overall)

        # Store health
        self.conn.cursor().execute("""
            INSERT INTO dashboard.dashboard_health (health_score, health_grade, status, calculated_at)
            VALUES (%s, %s, %s, NOW())
        """, (overall, g, "operational"))
        self.conn.commit()

        return {
            "health_score": overall,
            "health_grade": g,
            "knowledge_health": k_h,
            "governance_score": g_s,
            "automation_score": a_s,
            "status": "operational",
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

    def executive(self):
        rows = self._q("SELECT * FROM dashboard.mv_executive_metrics")
        r = dict(rows[0]) if rows else {}
        k_h = self._calc_knowledge_health()
        g_s = self._calc_governance_score()
        a_s = self._calc_automation_score()
        return {
            "knowledge_health_score": k_h,
            "knowledge_health_grade": grade(k_h),
            "governance_score": g_s,
            "governance_grade": grade(g_s),
            "automation_score": a_s,
            "automation_grade": grade(a_s),
            "total_records": r.get("total_records", 0),
            "curated_assets": r.get("curated_assets", 0),
            "principles": r.get("principles", 0),
            "policies": r.get("policies", 0),
            "rules": r.get("rules", 0),
            "sops": r.get("sops", 0),
            "open_contradictions": r.get("open_contradictions", 0),
            "resolved_contradictions": r.get("resolved_contradictions", 0),
            "avg_quality": r.get("avg_quality", 0),
        }

    def knowledge(self):
        rows = self._q("SELECT * FROM dashboard.mv_knowledge_metrics")
        return dict(rows[0]) if rows else {}

    def governance(self):
        rows = self._q("SELECT * FROM dashboard.mv_governance_metrics")
        return dict(rows[0]) if rows else {}

    def rcaf(self):
        rows = self._q("SELECT * FROM dashboard.mv_rcaf_metrics")
        return dict(rows[0]) if rows else {}

    def founder(self):
        rows = self._q("SELECT * FROM dashboard.mv_founder_intelligence LIMIT 20")
        return [dict(r) for r in rows]

    def top_assets(self):
        rows = self._q("""
            SELECT asset_name, category, quality_score, asset_type, status
            FROM knowledge.curated_assets
            ORDER BY quality_score DESC LIMIT 10
        """)
        return [dict(r) for r in rows]

    def metrics(self):
        return {
            "health": self.health(),
            "executive": self.executive(),
            "knowledge": self.knowledge(),
            "governance": self.governance(),
            "rcaf": self.rcaf(),
        }

    # ── Populate Metrics Table ──

    def populate(self):
        k_h = self._calc_knowledge_health()
        g_s = self._calc_governance_score()
        a_s = self._calc_automation_score()
        overall = round((k_h + g_s + a_s) / 3, 1)

        metrics = [
            ("knowledge_health_score", k_h, "KPI", "knowledge"),
            ("governance_score", g_s, "KPI", "governance"),
            ("automation_score", a_s, "KPI", "automation"),
            ("overall_health_score", overall, "KPI", "system"),
            ("total_records", self._count("knowledge.knowledge_registry") + self._count("decision.decision_registry") + self._count("failure.failure_registry") + self._count("lesson.lesson_registry") + self._count("agent.agent_memory_registry"), "count", "knowledge"),
            ("curated_assets", self._count("knowledge.curated_assets"), "count", "knowledge"),
            ("principles", self._count("governance.organizational_principles"), "count", "governance"),
            ("policies", self._count("governance.policy_registry"), "count", "governance"),
            ("rules", self._count("governance.rule_registry"), "count", "governance"),
            ("sops", self._count("governance.sop_library"), "count", "governance"),
            ("preventive_rules", self._count_where("agent.agent_memory_registry", "memory_type='constraint'"), "count", "rcaf"),
        ]

        cur = self.conn.cursor()
        for name, value, cat, group in metrics:
            cur.execute("""
                INSERT INTO dashboard.dashboard_metrics (metric_name, metric_value, metric_category, snapshot_time)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (metric_name) DO UPDATE
                SET metric_value = EXCLUDED.metric_value, snapshot_time = NOW()
            """, (name, value, f"{cat}:{group}"))

        # Snapshot
        exec_data = self.executive()
        cur.execute("""
            INSERT INTO dashboard.dashboard_snapshots
            (knowledge_health, governance_score, automation_score, total_records, curated_assets, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (k_h, g_s, a_s, exec_data["total_records"], exec_data["curated_assets"],
              f"Grade: {grade(overall)} | Avg: {exec_data['avg_quality']}"))

        self.conn.commit()
        return {"status": "populated", "metrics_count": len(metrics), "scores": {"knowledge": k_h, "governance": g_s, "automation": a_s, "overall": overall, "grade": grade(overall)}}

    def _count(self, table):
        cur = self.conn.cursor()
        cur.execute(f"SELECT count(*) FROM {table}")
        return cur.fetchone()[0]

    def _count_where(self, table, where):
        cur = self.conn.cursor()
        cur.execute(f"SELECT count(*) FROM {table} WHERE {where}")
        return cur.fetchone()[0]


def main():
    parser = argparse.ArgumentParser(description="Founder Dashboard API")
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--executive", action="store_true")
    parser.add_argument("--knowledge", action="store_true")
    parser.add_argument("--governance", action="store_true")
    parser.add_argument("--rcaf", action="store_true")
    parser.add_argument("--founder", action="store_true")
    parser.add_argument("--top-assets", action="store_true")
    parser.add_argument("--metrics", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--populate", action="store_true")
    args = parser.parse_args()

    api = DashboardAPI()
    try:
        enc = lambda o: float(o) if isinstance(o, Decimal) else o.isoformat() if isinstance(o, (datetime, date)) else str(o)
        if args.refresh:
            print(safe_json(api.refresh()))
        elif args.health:
            print(safe_json(api.health()))
        elif args.executive:
            print(safe_json(api.executive()))
        elif args.knowledge:
            print(safe_json(api.knowledge()))
        elif args.governance:
            print(safe_json(api.governance()))
        elif args.rcaf:
            print(safe_json(api.rcaf()))
        elif args.founder:
            print(safe_json(api.founder()))
        elif args.top_assets:
            print(safe_json(api.top_assets()))
        elif args.metrics:
            print(safe_json(api.metrics()))
        elif args.populate:
            print(safe_json(api.populate()))
        else:
            parser.print_help()
    finally:
        api.close()


if __name__ == "__main__":
    main()
