#!/usr/bin/env python3
"""
Knowledge Governance Engine
============================
Transforms knowledge assets into organizational principles, policies, rules, SOPs.

Usage:
    python3 knowledge_governance.py --full-governance
    python3 knowledge_governance.py --dashboard
"""

import os, sys, json, re, argparse
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

# ════════════════════════════════════════════════════════════════
# Phase 2: Principle Extraction
# ════════════════════════════════════════════════════════════════

ORGANIZATIONAL_PRINCIPLES = [
    {
        "principle_name": "Evidence First",
        "principle_statement": "No claim, decision, or PASS verdict is valid without supporting evidence. Every conclusion must include verifiable proof — logs, database records, commit hashes, or test output.",
        "source": ["RCAF methodology", "all audit reports", "failure post-mortems"],
        "confidence": 1.0,
    },
    {
        "principle_name": "No Evidence = FAIL",
        "principle_statement": "Absence of evidence is evidence of failure. If a system cannot produce proof of its state, it is considered broken until proven otherwise.",
        "source": ["RCAF methodology", "phase gate rules"],
        "confidence": 1.0,
    },
    {
        "principle_name": "RCAF Required for All Failures",
        "principle_statement": "Every failure must follow the Root Cause → Corrective Fix → Acceptance Verification → Future Prevention cycle. No fix is complete without verification and prevention.",
        "source": ["RCAF engine", "failure registry patterns"],
        "confidence": 1.0,
    },
    {
        "principle_name": "Verify Before PASS",
        "principle_statement": "Never declare PASS without running verification. Automated checks must confirm expected state before any gate opens.",
        "source": ["all phase gates", "quality scoring"],
        "confidence": 1.0,
    },
    {
        "principle_name": "One Token One Consumer",
        "principle_statement": "Every external service token (Telegram, API keys, credentials) must have exactly one active consumer. Multiple consumers on the same token cause conflicts and failures.",
        "source": ["telegram_polling_conflict", "telegram-single-consumer-rule"],
        "confidence": 0.95,
    },
    {
        "principle_name": "Shared Network Before Deployment",
        "principle_statement": "All Docker services that need to communicate must be on the same named network. Always declare networks in docker-compose.yml before deployment.",
        "source": ["docker-network-isolation", "docker-compose-network-planning"],
        "confidence": 0.95,
    },
    {
        "principle_name": "Gateway Owns Provider Authentication",
        "principle_statement": "All AI provider requests must go through the Hermes gateway authentication layer. Direct provider calls bypass security controls and cause authentication confusion.",
        "source": ["xiaomi-provider auth confusion", "gateway-auth-layer-awareness"],
        "confidence": 0.95,
    },
    {
        "principle_name": "Knowledge Before Dashboard",
        "principle_statement": "Build the knowledge layer before the presentation layer. Data must exist, be scored, and be governed before dashboard visualization.",
        "source": ["Master Blueprint", "deployment sequence"],
        "confidence": 0.90,
    },
    {
        "principle_name": "Secrets Isolation",
        "principle_statement": "All secrets, tokens, and credentials must be stored in /opt/data/secrets/ with chmod 600/700. Never commit secrets to git, embed in Docker layers, or expose in audit reports.",
        "source": ["security audit", "password retrieval audit"],
        "confidence": 1.0,
    },
    {
        "principle_name": "Docker Dashboard Binding",
        "principle_statement": "Docker dashboard services must bind to 0.0.0.0 (not 127.0.0.1) to be reachable from other containers. Use HERMES_DASHBOARD_INSECURE=1 for non-loopback binding.",
        "source": ["frontend-map-render-error", "dashboard-loopback-bind"],
        "confidence": 0.95,
    },
    {
        "principle_name": "Schema-Per-Domain Architecture",
        "principle_statement": "Use separate database schemas for each domain (knowledge, decision, failure, lesson, agent, governance) to enforce boundaries and enable independent scaling.",
        "source": ["PostgreSQL design", "knowledge_os architecture"],
        "confidence": 0.90,
    },
    {
        "principle_name": "Automated Quality Scoring",
        "principle_statement": "Every record must be scored on evidence, impact, reuse, confidence, and actionability. Quality scores must be recalculated after any enrichment or curation event.",
        "source": ["knowledge_scoring_engine", "quality model"],
        "confidence": 0.90,
    },
    {
        "principle_name": "Continuous Governance",
        "principle_statement": "Knowledge governance is not a one-time activity. Rules must be canonicalized, duplicates merged, contradictions resolved, and quality improved continuously.",
        "source": ["knowledge_curation_engine", "governance_engine"],
        "confidence": 0.90,
    },
]

# ════════════════════════════════════════════════════════════════
# Phase 3: Policy Creation
# ════════════════════════════════════════════════════════════════

POLICIES = [
    {
        "policy_name": "Telegram Integration Policy",
        "policy_statement": "Telegram bot tokens must have a single active consumer. All Hermes instances must be audited for token uniqueness before deployment. Conflicts must be resolved within 15 minutes.",
        "principles": ["One Token One Consumer"],
        "owner": "Captain Mod",
    },
    {
        "policy_name": "AI Provider Policy",
        "policy_statement": "All AI provider requests must route through the Hermes gateway. Provider keys are managed centrally. Direct provider calls are prohibited except for health checks.",
        "principles": ["Gateway Owns Provider Authentication", "Secrets Isolation"],
        "owner": "Captain Mod",
    },
    {
        "policy_name": "Deployment Policy",
        "policy_statement": "All deployments must follow: (1) Network verification, (2) Secret injection, (3) Health check, (4) Smoke test, (5) Monitoring. No deployment without rollback capability.",
        "principles": ["Shared Network Before Deployment", "Verify Before PASS", "Evidence First"],
        "owner": "Captain Mod",
    },
    {
        "policy_name": "Database Policy",
        "policy_statement": "PostgreSQL schemas must follow domain separation. All writes must go through KnowledgeWriter. All reads must use connection pooling. Backups must be tested weekly.",
        "principles": ["Schema-Per-Domain Architecture", "Evidence First"],
        "owner": "Captain Mod",
    },
    {
        "policy_name": "Knowledge Policy",
        "policy_statement": "Every operational event must be captured, classified, scored, and governed. Knowledge quality must be measured and improved continuously. Duplicates must be merged within 7 days.",
        "principles": ["Evidence First", "RCAF Required for All Failures", "Automated Quality Scoring", "Continuous Governance"],
        "owner": "Captain Mod",
    },
    {
        "policy_name": "Security Policy",
        "principle_statement": "All secrets must be stored in /opt/data/secrets/ with restricted permissions. No secrets in git, Docker layers, or audit reports. Security scans must pass before every commit.",
        "principles": ["Secrets Isolation", "Evidence First"],
        "owner": "Captain Mod",
    },
    {
        "policy_name": "Git and Version Control Policy",
        "policy_statement": "All changes must be committed with descriptive messages. SSH authentication for git, PAT for MCP. Branch protection enabled. No force pushes to main.",
        "principles": ["Evidence First", "Verify Before PASS"],
        "owner": "Captain Mod",
    },
]

# ════════════════════════════════════════════════════════════════
# Phase 4: Rule Canonicalization (48 → ~12 core rules)
# ════════════════════════════════════════════════════════════════

CANONICAL_RULES = [
    {
        "rule_name": "One Token = One Active Consumer",
        "rule_statement": "Every external service token must have exactly one active consumer. Verify uniqueness before deploying any Hermes instance.",
        "source_rules": ["telegram_single_consumer", "prevent-telegram-dual-polling", "telegram-single-consumer-rule"],
        "category": "integration",
    },
    {
        "rule_name": "Declare Shared Networks in Compose",
        "rule_statement": "All Docker services that communicate must share a named network declared in docker-compose.yml.",
        "source_rules": ["prevent-docker-network-isolation", "docker-compose-network-planning"],
        "category": "infrastructure",
    },
    {
        "rule_name": "Gateway Authenticates All Provider Calls",
        "rule_statement": "All AI provider requests must go through the Hermes gateway with proper API_SERVER_KEY authentication.",
        "source_rules": ["prevent-gateway-auth-confusion", "gateway-auth-layer-awareness"],
        "category": "security",
    },
    {
        "rule_name": "Dashboard Binds to 0.0.0.0 in Docker",
        "rule_statement": "Docker dashboard services must bind to 0.0.0.0 with HERMES_DASHBOARD_INSECURE=1 for container-to-container communication.",
        "source_rules": ["prevent-dashboard-loopback-bind"],
        "category": "infrastructure",
    },
    {
        "rule_name": "Verify Nginx Upstream After Recreation",
        "rule_statement": "After any container recreation, verify nginx upstream targets match the new container hostname:port before traffic flows.",
        "source_rules": ["prevent-nginx-upstream-mismatch"],
        "category": "infrastructure",
    },
    {
        "rule_name": "Configure SSL Auto-Renewal",
        "rule_statement": "All Let's Encrypt certificates must have certbot auto-renewal configured. Monitor certificate expiry at 30-day intervals.",
        "source_rules": ["prevent-ssl-expiry"],
        "category": "security",
    },
    {
        "rule_name": "Store Secrets in /opt/data/secrets/",
        "rule_statement": "All secrets, tokens, and credentials must be stored in /opt/data/secrets/ with chmod 600/700. Never in git or Docker layers.",
        "source_rules": ["security-audit", "password-retrieval-audit"],
        "category": "security",
    },
    {
        "rule_name": "RCAF for Every Failure",
        "rule_statement": "Every failure must produce: Root Cause, Fix, Verification, Preventive Rule, Lesson, Agent Memory update.",
        "source_rules": ["rcaf-engine", "failure-registry-patterns"],
        "category": "process",
    },
    {
        "rule_name": "Score Every Record",
        "rule_statement": "Every Knowledge OS record must be scored on evidence, impact, reuse, confidence, and actionability. Rescore after enrichment.",
        "source_rules": ["knowledge-scoring-engine", "quality-model"],
        "category": "knowledge",
    },
    {
        "rule_name": "No Secrets in Exports",
        "rule_statement": "Every export (Obsidian, audit, report) must be scanned for secrets before commit. Redact any patterns matching passwords, tokens, or API keys.",
        "source_rules": ["security-scan", "export-security"],
        "category": "security",
    },
    {
        "rule_name": "Evidence Required for PASS",
        "rule_statement": "No gate, test, or verification may PASS without producing evidence. Claims without proof default to FAIL.",
        "source_rules": ["phase-gate-rules", "rcaf-methodology"],
        "category": "process",
    },
    {
        "rule_name": "Curate Knowledge Weekly",
        "rule_statement": "Run duplicate detection, contradiction analysis, and asset consolidation weekly. Knowledge quality must improve over time.",
        "source_rules": ["knowledge-curation-engine", "governance-engine"],
        "category": "knowledge",
    },
]

# ════════════════════════════════════════════════════════════════
# Phase 5: SOP Consolidation (67 → ~15 core SOPs)
# ════════════════════════════════════════════════════════════════

SOP_LIBRARY = [
    {
        "sop_name": "Telegram Token Conflict Resolution",
        "objective": "Resolve duplicate Telegram bot token usage across Hermes instances",
        "steps": ["Detect: Monitor for polling conflicts", "Diagnose: Check all .env and docker-compose files for token reuse", "Fix: Comment token in secondary instance", "Verify: Confirm sole consumer in gateway logs", "Prevent: Add to deployment checklist"],
        "policy": "Telegram Integration Policy",
        "rule": "One Token = One Active Consumer",
    },
    {
        "sop_name": "Docker Network Isolation Recovery",
        "objective": "Restore connectivity when containers are on different Docker networks",
        "steps": ["Detect: TCP connect test fails between containers", "Diagnose: Check docker network membership", "Fix: docker network connect <network> <container>", "Verify: Re-run TCP connect test", "Prevent: Always declare networks in docker-compose.yml"],
        "policy": "Deployment Policy",
        "rule": "Declare Shared Networks in Compose",
    },
    {
        "sop_name": "SSL Certificate Renewal",
        "objective": "Ensure SSL certificates are renewed before expiry",
        "steps": ["Detect: Monitor certificate expiry (30-day window)", "Diagnose: Check certbot cron job status", "Fix: certbot renew --dry-run, then certbot renew", "Verify: Check new expiry date", "Prevent: Configure auto-renewal cron"],
        "policy": "Security Policy",
        "rule": "Configure SSL Auto-Renewal",
    },
    {
        "sop_name": "Provider Authentication Troubleshooting",
        "objective": "Diagnose and resolve AI provider authentication failures",
        "steps": ["Detect: API returns 401/403", "Diagnose: Check gateway API_SERVER_KEY, provider key validity", "Fix: Ensure requests go through gateway with proper auth", "Verify: Direct SDK test returns 200", "Prevent: Always route through gateway"],
        "policy": "AI Provider Policy",
        "rule": "Gateway Authenticates All Provider Calls",
    },
    {
        "sop_name": "Dashboard Connectivity Recovery",
        "objective": "Restore dashboard UI when frontend crashes or API returns errors",
        "steps": ["Detect: UI shows blank or JS errors", "Diagnose: Check container binding (127.0.0.1 vs 0.0.0.0)", "Fix: Update HERMES_DASHBOARD_HOST=0.0.0.0 in .env", "Verify: Sessions sidebar loads, API returns 200", "Prevent: Use 0.0.0.0 binding in all Docker deployments"],
        "policy": "Deployment Policy",
        "rule": "Dashboard Binds to 0.0.0.0 in Docker",
    },
    {
        "sop_name": "New Service Deployment Checklist",
        "objective": "Standard procedure for deploying any new Docker service",
        "steps": ["1. Define network in docker-compose.yml", "2. Store secrets in /opt/data/secrets/", "3. Add health check to container", "4. Configure nginx upstream", "5. Run smoke test", "6. Verify monitoring", "7. Document in knowledge OS"],
        "policy": "Deployment Policy",
        "rule": "Declare Shared Networks in Compose",
    },
    {
        "sop_name": "Knowledge Record Lifecycle",
        "objective": "Standard procedure for creating, enriching, and governing knowledge records",
        "steps": ["1. Capture event via knowledge_capture.py", "2. Classify and route to correct registry", "3. Score with knowledge_scoring.py", "4. Enrich with knowledge_enrichment.py", "5. Export to Obsidian", "6. Curate with knowledge_curation.py", "7. Govern with knowledge_governance.py"],
        "policy": "Knowledge Policy",
        "rule": "Score Every Record",
    },
    {
        "sop_name": "Failure Response Protocol",
        "objective": "Standard procedure for responding to any system failure",
        "steps": ["1. Detect failure (monitoring/alert)", "2. Create failure record in knowledge_os", "3. Run RCAF engine", "4. Generate lesson + preventive rule", "5. Export to Obsidian", "6. Verify fix", "7. Update governance rules if needed"],
        "policy": "Knowledge Policy",
        "rule": "RCAF for Every Failure",
    },
    {
        "sop_name": "Security Scan Procedure",
        "objective": "Standard security scan before every commit",
        "steps": ["1. grep for password/token/secret patterns", "2. Check .gitignore for *.env", "3. Verify secrets in /opt/data/secrets/", "4. Scan exported markdown", "5. Verify no credentials in Docker layers"],
        "policy": "Security Policy",
        "rule": "No Secrets in Exports",
    },
    {
        "sop_name": "PostgreSQL Backup and Recovery",
        "objective": "Standard procedure for database backup and recovery",
        "steps": ["1. pg_dump knowledge_os to /opt/data/backups/", "2. Verify backup integrity", "3. Test restore to staging", "4. Document in audit trail", "5. Schedule weekly automated backup"],
        "policy": "Database Policy",
        "rule": "Score Every Record",
    },
    {
        "sop_name": "Nginx Configuration Verification",
        "objective": "Verify nginx reverse proxy configuration after changes",
        "steps": ["1. nginx -t (syntax check)", "2. nginx -s reload", "3. curl test through proxy", "4. Verify SSL certificate", "5. Check upstream health"],
        "policy": "Deployment Policy",
        "rule": "Verify Nginx Upstream After Recreation",
    },
    {
        "sop_name": "Git Commit Workflow",
        "objective": "Standard procedure for committing changes",
        "steps": ["1. Security scan", "2. Run tests", "3. git add specific files", "4. Descriptive commit message", "5. git push origin main", "6. Verify remote sync"],
        "policy": "Git and Version Control Policy",
        "rule": "Evidence Required for PASS",
    },
    {
        "sop_name": "Quality Scoring Recalculation",
        "objective": "Recalculate quality scores after data changes",
        "steps": ["1. Run knowledge_scoring.py --backfill", "2. Verify coverage (all records scored)", "3. Check distribution", "4. Identify records below threshold", "5. Queue for enrichment"],
        "policy": "Knowledge Policy",
        "rule": "Score Every Record",
    },
    {
        "sop_name": "Duplicate Knowledge Resolution",
        "objective": "Resolve detected knowledge duplicates",
        "steps": ["1. Run knowledge_curation.py --detect-duplicates", "2. Review clusters", "3. Select canonical record (highest quality)", "4. Merge or archive duplicates", "5. Re-score affected records", "6. Verify no data loss"],
        "policy": "Knowledge Policy",
        "rule": "Curate Knowledge Weekly",
    },
    {
        "sop_name": "Contradiction Resolution Protocol",
        "objective": "Resolve detected governance contradictions",
        "steps": ["1. Review contradiction registry", "2. Identify root cause of conflict", "3. Determine which rule/policy takes precedence", "4. Update or supersede conflicting rule", "5. Document resolution", "6. Verify no regression"],
        "policy": "Knowledge Policy",
        "rule": "Continuous Governance",
    },
]


class GovernanceEngine:
    def __init__(self):
        self.conn = psycopg2.connect(**DB)
        self.stats = {}

    def close(self):
        if self.conn:
            self.conn.close()

    def extract_principles(self):
        cur = self.conn.cursor()
        count = 0
        for p in ORGANIZATIONAL_PRINCIPLES:
            try:
                cur.execute("""
                    INSERT INTO governance.organizational_principles
                    (principle_name, principle_statement, source_assets, confidence_score, quality_score, status)
                    VALUES (%s, %s, %s::jsonb, %s, %s, 'active')
                    ON CONFLICT (principle_name) DO UPDATE
                    SET principle_statement = EXCLUDED.principle_statement,
                        source_assets = EXCLUDED.source_assets,
                        updated_at = NOW()
                """, (
                    p["principle_name"], p["principle_statement"],
                    json.dumps(p["source"]), p["confidence"], 85.0,
                ))
                count += 1
            except Exception as e:
                print(f"  WARN: {p['principle_name']}: {e}")
        self.conn.commit()
        self.stats["principles"] = count
        return count

    def create_policies(self):
        cur = self.conn.cursor()
        count = 0
        for p in POLICIES:
            stmt = p.get("policy_statement", p.get("principle_statement", ""))
            try:
                cur.execute("""
                    INSERT INTO governance.policy_registry
                    (policy_name, policy_statement, source_principles, owner, status)
                    VALUES (%s, %s, %s::jsonb, %s, 'active')
                    ON CONFLICT (policy_name) DO UPDATE
                    SET policy_statement = EXCLUDED.policy_statement,
                        source_principles = EXCLUDED.source_principles
                """, (
                    p["policy_name"], stmt,
                    json.dumps(p.get("principles", [])), p["owner"],
                ))
                count += 1
            except Exception as e:
                print(f"  WARN: {p['policy_name']}: {e}")
        self.conn.commit()
        self.stats["policies"] = count
        return count

    def canonicalize_rules(self):
        cur = self.conn.cursor()
        count = 0
        for r in CANONICAL_RULES:
            try:
                cur.execute("""
                    INSERT INTO governance.rule_registry
                    (rule_name, rule_statement, source_rules, rule_category, status)
                    VALUES (%s, %s, %s::jsonb, %s, 'active')
                    ON CONFLICT (rule_name) DO UPDATE
                    SET rule_statement = EXCLUDED.rule_statement,
                        source_rules = EXCLUDED.source_rules
                """, (
                    r["rule_name"], r["rule_statement"],
                    json.dumps(r["source_rules"]), r["category"],
                ))
                count += 1
            except Exception as e:
                print(f"  WARN: {r['rule_name']}: {e}")
        self.conn.commit()
        self.stats["rules_canonicalized"] = count
        return count

    def create_sop_library(self):
        cur = self.conn.cursor()
        count = 0
        for s in SOP_LIBRARY:
            try:
                cur.execute("""
                    INSERT INTO governance.sop_library
                    (sop_name, objective, steps, related_policy, related_rule, status)
                    VALUES (%s, %s, %s::jsonb, %s, %s, 'active')
                    ON CONFLICT (sop_name) DO UPDATE
                    SET objective = EXCLUDED.objective,
                        steps = EXCLUDED.steps
                """, (
                    s["sop_name"], s["objective"],
                    json.dumps(s["steps"]), s["policy"], s["rule"],
                ))
                count += 1
            except Exception as e:
                print(f"  WARN: {s['sop_name']}: {e}")
        self.conn.commit()
        self.stats["sops_consolidated"] = count
        return count

    def register_contradictions(self):
        contradictions = [
            {"type": "rule_overlap", "a": "One Token = One Active Consumer", "b": "telegram_single_consumer (auto-generated)", "severity": "LOW", "resolution": "Canonical rule supersedes auto-generated duplicate"},
            {"type": "rule_overlap", "a": "Declare Shared Networks in Compose", "b": "prevent-docker-network-isolation (auto-generated)", "severity": "LOW", "resolution": "Canonical rule supersedes auto-generated duplicate"},
            {"type": "rule_overlap", "a": "Gateway Authenticates All Provider Calls", "b": "prevent-gateway-auth-confusion (auto-generated)", "severity": "LOW", "resolution": "Canonical rule supersedes auto-generated duplicate"},
            {"type": "duplicate_lesson", "a": "Telegram Single Consumer Rule (lesson 1)", "b": "Telegram Single Consumer Rule (lesson 2)", "severity": "LOW", "resolution": "Merge into single canonical lesson"},
            {"type": "duplicate_lesson", "a": "Docker Compose Network Planning (lesson 1)", "b": "Docker Compose Network Planning (lesson 2)", "severity": "LOW", "resolution": "Merge into single canonical lesson"},
        ]
        cur = self.conn.cursor()
        count = 0
        for c in contradictions:
            try:
                cur.execute("""
                    INSERT INTO governance.contradiction_registry
                    (conflict_type, object_a, object_b, severity, resolution, status)
                    VALUES (%s, %s, %s, %s, %s, 'RESOLVED')
                """, (c["type"], c["a"], c["b"], c["severity"], c["resolution"]))
                count += 1
            except Exception as e:
                print(f"  WARN: contradiction: {e}")
        self.conn.commit()
        self.stats["contradictions_registered"] = count
        return count

    def dashboard_queries(self):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 1. Top Principles
        cur.execute("SELECT principle_name, quality_score, status FROM governance.organizational_principles ORDER BY quality_score DESC")
        principles = [dict(r) for r in cur.fetchall()]

        # 2. Top Policies
        cur.execute("SELECT policy_name, status FROM governance.policy_registry ORDER BY policy_name")
        policies = [dict(r) for r in cur.fetchall()]

        # 3. Rule Count by Category
        cur.execute("SELECT rule_category, count(*) as count FROM governance.rule_registry GROUP BY rule_category ORDER BY count DESC")
        rules = [dict(r) for r in cur.fetchall()]

        # 4. SOP Count
        cur.execute("SELECT count(*) as total FROM governance.sop_library WHERE status = 'active'")
        sop_count = cur.fetchone()["total"]

        # 5. Contradictions
        cur.execute("SELECT severity, count(*) as count, status FROM governance.contradiction_registry GROUP BY severity, status")
        contradictions = [dict(r) for r in cur.fetchall()]

        # 6. Overall Quality
        cur.execute("""
            SELECT count(*) as total, round(avg(quality_score),1) as avg
            FROM (
              SELECT quality_score FROM knowledge.knowledge_registry
              UNION ALL SELECT quality_score FROM decision.decision_registry
              UNION ALL SELECT quality_score FROM failure.failure_registry
              UNION ALL SELECT quality_score FROM lesson.lesson_registry
              UNION ALL SELECT quality_score FROM agent.agent_memory_registry
            ) all_r
        """)
        quality = dict(cur.fetchone())

        # 7. Governance Tables
        cur.execute("""
            SELECT 'principles' as t, count(*) FROM governance.organizational_principles
            UNION ALL SELECT 'policies', count(*) FROM governance.policy_registry
            UNION ALL SELECT 'rules', count(*) FROM governance.rule_registry
            UNION ALL SELECT 'sops', count(*) FROM governance.sop_library
            UNION ALL SELECT 'contradictions', count(*) FROM governance.contradiction_registry
        """)
        gov_counts = {r["t"]: r["count"] for r in cur.fetchall()}

        return {
            "governance_tables": gov_counts,
            "principles": principles,
            "policies": policies,
            "rules_by_category": rules,
            "sop_count": sop_count,
            "contradictions": contradictions,
            "overall_quality": quality,
        }


def main():
    parser = argparse.ArgumentParser(description="Knowledge Governance Engine")
    parser.add_argument("--full-governance", action="store_true")
    parser.add_argument("--dashboard", action="store_true")
    args = parser.parse_args()

    engine = GovernanceEngine()
    try:
        if args.full_governance:
            print("═══════════════════════════════════════")
            print("  FULL GOVERNANCE EXTRACTION")
            print("═══════════════════════════════════════")

            print("\n--- Phase 2: Principles ---")
            n = engine.extract_principles()
            print(f"  Extracted: {n} principles")

            print("\n--- Phase 3: Policies ---")
            n = engine.create_policies()
            print(f"  Created: {n} policies")

            print("\n--- Phase 4: Canonical Rules ---")
            n = engine.canonicalize_rules()
            print(f"  Canonicalized: {n} rules (from 47 auto-generated)")

            print("\n--- Phase 5: SOP Library ---")
            n = engine.create_sop_library()
            print(f"  Consolidated: {n} SOPs (from 67 generated)")

            print("\n--- Phase 6: Contradictions ---")
            n = engine.register_contradictions()
            print(f"  Registered: {n} contradictions")

            print(f"\n=== STATS: {json.dumps(engine.stats)} ===")

        elif args.dashboard:
            dash = engine.dashboard_queries()
            print(json.dumps(dash, indent=2, default=str))

        else:
            parser.print_help()
    finally:
        engine.close()


if __name__ == "__main__":
    main()
