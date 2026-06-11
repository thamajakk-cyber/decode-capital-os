#!/usr/bin/env python3
"""
CAPTAIN MOD OS — News Knowledge Capture Engine
Converts approved news into structured knowledge.

Usage:
    python3 news_knowledge_capture.py --backfill       # Process all approved news
    python3 news_knowledge_capture.py --backfill --limit 50  # Process up to 50
    python3 news_knowledge_capture.py --stats          # Show statistics
    python3 news_knowledge_capture.py --patterns       # Detect market patterns
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

# ── Configuration ──
PG_CONTAINER = 'knowledge-os-postgres'
PG_USER = 'knowledge_admin'
PG_DB = 'knowledge_os'

# ── Event Type Classification ──
EVENT_TYPES = {
    'fed': {'importance': 'critical', 'impact': 'high'},
    'cpi': {'importance': 'critical', 'impact': 'high'},
    'nfp': {'importance': 'critical', 'impact': 'high'},
    'earnings': {'importance': 'high', 'impact': 'medium'},
    'geopolitical': {'importance': 'high', 'impact': 'medium'},
    'technical': {'importance': 'medium', 'impact': 'medium'},
    'sentiment': {'importance': 'medium', 'impact': 'low'},
    'regulation': {'importance': 'medium', 'impact': 'medium'},
    'macro': {'importance': 'high', 'impact': 'high'},
    'crypto': {'importance': 'medium', 'impact': 'medium'},
    'general': {'importance': 'low', 'impact': 'low'},
}

# ── SMC Context Templates ──
SMC_TEMPLATES = {
    'fed': 'FED decision impacts liquidity environment. Key levels: FVG, OB, BOS zones shift. Watch for institutional repositioning.',
    'cpi': 'CPI data shifts inflation narrative. Order blocks around key prints. SMC structure: BOS/MSS at macro level.',
    'nfp': 'NFP creates short-term volatility. Liquidity sweeps likely. Institutional flow: watch for displacement candles.',
    'earnings': 'Earnings create sector rotation. SMC: gap fills, order blocks at earnings levels. Liquidity pools at extremes.',
    'geopolitical': 'Geopolitical risk reprices assets. SMC: structure breaks, FVG expansion. Safe haven flows.',
    'technical': 'Technical levels drive SMC structure. Key: OB, FVG, BOS/MSS alignment. Institutional zones.',
    'sentiment': 'Sentiment shift drives positioning. SMC: liquidity hunts, stop runs. Contrarian zones.',
    'regulation': 'Regulation changes structural flows. SMC: re-rating zones, new order blocks.',
    'macro': 'Macro event shifts multi-timeframe structure. SMC: HTF BOS, institutional repositioning.',
    'crypto': 'Crypto-native events. SMC: on-chain liquidity, exchange order books. Structure at extremes.',
    'general': 'General market event. SMC: standard structure analysis. Multi-timeframe confluence.',
}


def pg_query(sql):
    """Execute PostgreSQL query and return rows."""
    cmd = ['docker', 'exec', PG_CONTAINER,
           'psql', '-U', PG_USER, '-d', PG_DB,
           '-t', '-A', '-F', '|', '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    rows = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            rows.append(line.split('|'))
    return rows


def pg_execute(sql):
    """Execute PostgreSQL statement."""
    cmd = ['docker', 'exec', PG_CONTAINER,
           'psql', '-U', PG_USER, '-d', PG_DB,
           '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def get_approved_news():
    """Get all approved news not yet processed into knowledge."""
    rows = pg_query(
        "SELECT id, headline, source, event_type, importance, market_impact, smc_context "
        "FROM news.approved_news "
        "WHERE id NOT IN (SELECT event_id FROM news.news_knowledge_registry WHERE event_id IS NOT NULL) "
        "ORDER BY approved_at DESC"
    )
    return rows


def get_all_approved_news(limit=None):
    """Get all approved news for backfill."""
    sql = (
        "SELECT id, headline, source, event_type, importance, market_impact, smc_context "
        "FROM news.approved_news ORDER BY approved_at DESC"
    )
    if limit:
        sql += " LIMIT " + str(limit)
    return pg_query(sql)


def classify_event(headline, event_type):
    """Classify event importance and impact."""
    headline_lower = headline.lower()

    # Detect from headline keywords
    if any(w in headline_lower for w in ['fed', 'fomc', 'rate', 'interest']):
        return 'fed', 'critical', 'high'
    if any(w in headline_lower for w in ['cpi', 'inflation', 'pce']):
        return 'cpi', 'critical', 'high'
    if any(w in headline_lower for w in ['nfp', 'payroll', 'unemployment', 'jobs']):
        return 'nfp', 'critical', 'high'
    if any(w in headline_lower for w in ['earnings', 'revenue', 'profit', 'eps']):
        return 'earnings', 'high', 'medium'
    if any(w in headline_lower for w in ['war', 'conflict', 'sanction', 'geopolit']):
        return 'geopolitical', 'high', 'medium'
    if any(w in headline_lower for w in ['crypto', 'bitcoin', 'btc', 'eth']):
        return 'crypto', 'medium', 'medium'
    if any(w in headline_lower for w in ['regulation', 'sec', 'ruling', 'ban']):
        return 'regulation', 'medium', 'medium'

    # Use provided event_type or default
    if event_type and event_type != 'general':
        template = EVENT_TYPES.get(event_type, EVENT_TYPES['general'])
        return event_type, template['importance'], template['impact']

    return 'general', 'low', 'low'


def generate_market_context(headline, event_type):
    """Generate market impact context."""
    template = SMC_TEMPLATES.get(event_type, SMC_TEMPLATES['general'])
    headline_lower = headline.lower()

    impacts = []
    if any(w in headline_lower for w in ['bullish', 'surge', 'rally', 'up']):
        impacts.append('Bullish momentum expected. Watch for continuation structures.')
    if any(w in headline_lower for w in ['bearish', 'crash', 'drop', 'down', 'fall']):
        impacts.append('Bearish pressure expected. Watch for displacement and FVG expansion.')
    if any(w in headline_lower for w in ['volatile', 'volatility', 'swing']):
        impacts.append('Increased volatility. Liquidity sweeps likely at extremes.')
    if any(w in headline_lower for w in ['hawkish', 'tightening']):
        impacts.append('Hawkish shift. DXY strength, risk-off flows.')
    if any(w in headline_lower for w in ['dovish', 'easing', 'cut']):
        impacts.append('Dovish shift. Risk-on flows, equity strength.')

    context = template
    if impacts:
        context += ' Specific: ' + ' '.join(impacts)
    return context


def generate_smc_context(headline, event_type):
    """Generate SMC-specific context."""
    smc = SMC_TEMPLATES.get(event_type, SMC_TEMPLATES['general'])
    return smc


def generate_decision_context(headline, event_type, importance):
    """Generate decision-making context."""
    if importance == 'critical':
        return ('CRITICAL EVENT — High conviction setups preferred. '
                'Wait for H4/H1 structure confirmation before entry. '
                'Risk management: reduced position size, wider stops.')
    elif importance == 'high':
        return ('HIGH IMPACT — Standard position sizing. '
                'Look for M15/M5 entry confirmations. '
                'Prefer trend continuation after structure forms.')
    elif importance == 'medium':
        return ('MEDIUM IMPACT — Small position sizing. '
                'Intraday setups only. Quick profit targets.')
    else:
        return ('LOW IMPACT — Monitor only. No new positions. '
                'Use for context building.')


def generate_lesson(headline, event_type, outcome=None):
    """Generate lesson from news event."""
    if outcome:
        if 'success' in str(outcome).lower() or 'pass' in str(outcome).lower():
            return ('Lesson: ' + event_type.upper() + ' event analysis was accurate. '
                    'Pattern: trust the SMC structure alignment for ' + event_type + ' events.')
        elif 'fail' in str(outcome).lower():
            return ('Lesson: ' + event_type.upper() + ' event analysis missed key context. '
                    'Pattern: always cross-reference with HTF structure before entry.')

    return ('Lesson: ' + event_type.upper() + ' events require multi-timeframe SMC confirmation. '
            'Key: BOS + FVG alignment on H4 before M15 entry.')


def calculate_quality_score(headline, event_type, importance, has_smc=True):
    """Calculate quality score (0-100)."""
    score = 0

    # Evidence (20)
    if headline and len(headline) > 20:
        score += 10
    if has_smc:
        score += 10

    # Impact (20)
    impact_map = {'critical': 20, 'high': 15, 'medium': 10, 'low': 5}
    score += impact_map.get(importance, 5)

    # Reuse (20) — pattern-based events have higher reuse
    reusable_types = ['fed', 'cpi', 'nfp', 'earnings']
    score += 15 if event_type in reusable_types else 8

    # Confidence (20)
    score += 12  # Default confidence for structured knowledge

    # Actionability (20)
    actionable_types = ['fed', 'cpi', 'nfp', 'macro', 'technical']
    score += 15 if event_type in actionable_types else 10

    return min(score, 100)


def get_grade(score):
    """Convert score to grade."""
    if score >= 95: return 'A+'
    if score >= 90: return 'A'
    if score >= 80: return 'B'
    if score >= 70: return 'C'
    if score >= 60: return 'D'
    return 'F'


def store_knowledge(event_id, headline, source, event_type, importance,
                    market_impact, smc_context, decision_context, outcome, lesson,
                    quality_score, quality_grade):
    """Insert knowledge record into news_knowledge_registry."""
    # Escape single quotes
    def esc(s):
        if s is None:
            return 'NULL'
        return "'" + str(s).replace("'", "''") + "'"

    sql = (
        "INSERT INTO news.news_knowledge_registry "
        "(event_id, headline, source, event_type, importance, market_impact, "
        "smc_context, decision_context, outcome, lesson, "
        "quality_score, quality_grade, evidence_score, impact_score, "
        "reuse_score, confidence_score, actionability_score) "
        "VALUES ("
        + esc(event_id) + ", "
        + esc(headline) + ", "
        + esc(source) + ", "
        + esc(event_type) + ", "
        + esc(importance) + ", "
        + esc(market_impact) + ", "
        + esc(smc_context) + ", "
        + esc(decision_context) + ", "
        + esc(outcome) + ", "
        + esc(lesson) + ", "
        + str(quality_score) + ", "
        + esc(quality_grade) + ", "
        + str(min(20, quality_score // 5)) + ", "
        + str(min(20, quality_score // 5)) + ", "
        + str(min(20, quality_score // 5)) + ", "
        + str(min(20, quality_score // 5)) + ", "
        + str(min(20, quality_score // 5)) +
        ") RETURNING id"
    )
    return pg_query(sql)


def backfill_knowledge(limit=None):
    """Process approved news into knowledge records."""
    print("── Backfilling News Knowledge ──")

    news_items = get_all_approved_news(limit)
    print("  Approved news found: " + str(len(news_items)))

    if not news_items:
        print("  No approved news to process.")
        return 0

    created = 0
    for item in news_items:
        event_id = item[0]
        headline = item[1]
        source = item[2]
        event_type = item[3]
        importance = item[4]
        market_impact = item[5]
        smc_context = item[6]

        # Classify if needed
        if not event_type or event_type == 'general':
            event_type, importance, impact = classify_event(headline, event_type)
        else:
            _, importance, impact = classify_event(headline, event_type)

        # Generate contexts
        if not market_impact:
            market_impact = generate_market_context(headline, event_type)
        if not smc_context:
            smc_context = generate_smc_context(headline, event_type)

        decision_context = generate_decision_context(headline, event_type, importance)
        lesson = generate_lesson(headline, event_type)
        quality_score = calculate_quality_score(headline, event_type, importance)
        quality_grade = get_grade(quality_score)

        # Store
        result = store_knowledge(
            event_id, headline, source, event_type, importance,
            market_impact, smc_context, decision_context, None, lesson,
            quality_score, quality_grade
        )

        if result and len(result) > 0:
            created += 1
        else:
            print("  ERROR: Failed to store: " + headline[:60])

    print("  Knowledge records created: " + str(created))
    return created


def show_stats():
    """Show news knowledge statistics."""
    print("\n── News Knowledge Statistics ──")

    tables = [
        ("raw_news", "news.raw_news"),
        ("filtered_news", "news.filtered_news"),
        ("approved_news", "news.approved_news"),
        ("knowledge_records", "news.news_knowledge_registry"),
        ("market_patterns", "news.market_patterns"),
    ]

    for label, table in tables:
        rows = pg_query("SELECT count(*) FROM " + table)
        count = rows[0][0] if rows else "0"
        print("  " + label + ": " + str(count))

    # Quality distribution
    print("\n── Quality Distribution ──")
    rows = pg_query(
        "SELECT quality_grade, count(*) FROM news.news_knowledge_registry "
        "GROUP BY quality_grade ORDER BY count DESC"
    )
    for row in rows:
        print("  " + row[0] + ": " + row[1])

    # Top knowledge
    print("\n── Top Knowledge (by quality) ──")
    rows = pg_query(
        "SELECT headline, event_type, quality_score, quality_grade "
        "FROM news.news_knowledge_registry ORDER BY quality_score DESC LIMIT 5"
    )
    for row in rows:
        print("  [" + row[3] + " " + row[2] + "] " + row[1] + ": " + row[0][:60])

    # Average quality
    rows = pg_query("SELECT avg(quality_score) FROM news.news_knowledge_registry")
    avg = rows[0][0] if rows else "N/A"
    print("\n  Average quality: " + str(avg))


def detect_patterns():
    """Detect market patterns from knowledge records."""
    print("\n── Detecting Market Patterns ──")

    # Pattern: Event type frequency
    rows = pg_query(
        "SELECT event_type, count(*), avg(quality_score) "
        "FROM news.news_knowledge_registry "
        "GROUP BY event_type HAVING count(*) >= 1 "
        "ORDER BY count DESC"
    )

    created = 0
    for row in rows:
        event_type = row[0]
        count = int(row[1])
        avg_quality = float(row[2]) if row[2] else 0

        # Check if pattern already exists
        existing = pg_query(
            "SELECT id FROM news.market_patterns WHERE pattern_name = '" + event_type + "_frequency'"
        )

        if existing:
            # Update
            pg_query(
                "UPDATE news.market_patterns SET "
                "occurrences = " + str(count) + ", "
                "last_seen = now(), "
                "quality_score = " + str(avg_quality) + " "
                "WHERE pattern_name = '" + event_type + "_frequency'"
            )
        else:
            # Create
            pg_query(
                "INSERT INTO news.market_patterns "
                "(pattern_name, pattern_type, description, occurrences, quality_score) "
                "VALUES ('" + event_type + "_frequency', 'event_frequency', "
                "'" + event_type + " events occur " + str(count) + " times', "
                + str(count) + ", " + str(avg_quality) + ")"
            )
            created += 1

    print("  Patterns created: " + str(created))

    # Show patterns
    rows = pg_query(
        "SELECT pattern_name, occurrences, quality_score, status "
        "FROM news.market_patterns ORDER BY occurrences DESC"
    )
    for row in rows:
        print("  " + row[0] + ": " + row[1] + " occurrences (quality: " + row[2] + ")")


def main():
    parser = argparse.ArgumentParser(description='News Knowledge Capture Engine')
    parser.add_argument('--backfill', action='store_true', help='Backfill knowledge from approved news')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of records to process')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--patterns', action='store_true', help='Detect market patterns')
    args = parser.parse_args()

    if not any([args.backfill, args.stats, args.patterns]):
        parser.print_help()
        sys.exit(1)

    start = datetime.utcnow()
    print("=" * 60)
    print("NEWS KNOWLEDGE CAPTURE ENGINE — " + start.strftime('%Y-%m-%d %H:%M:%S UTC'))
    print("=" * 60)

    if args.backfill:
        count = backfill_knowledge(args.limit)
        print("\nBackfill: " + str(count) + " records created")

    if args.stats:
        show_stats()

    if args.patterns:
        detect_patterns()

    elapsed = (datetime.utcnow() - start).total_seconds()
    print("\nCompleted in " + str(round(elapsed, 1)) + "s")


if __name__ == '__main__':
    main()
