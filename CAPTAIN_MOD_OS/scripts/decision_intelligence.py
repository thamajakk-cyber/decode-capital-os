#!/usr/bin/env python3
"""Decision Intelligence Engine — Decision Support Only."""
import argparse
import json
import subprocess

PG_CONTAINER = 'knowledge-os-postgres'
PG_USER = 'knowledge_admin'
PG_DB = 'knowledge_os'


def pg_query_values(sql, columns):
    result = subprocess.run(
        ['docker', 'exec', PG_CONTAINER, 'psql', '-U', PG_USER, '-d', PG_DB, '-t', '-A', '-c', sql],
        capture_output=True, text=True
    )
    rows = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('|')
        rows.append(dict(zip(columns, parts)))
    return rows


def run_context(event_type, market_context='default'):
    pat_cols = ['event_type','pattern_name','pattern_id','occurrences','confidence_score','status','source_outcome_ids','win_rate','bias_accuracy','liquidity_accuracy','false_signal_rate','narrative_accuracy']
    pat_sql = (
        "SELECT pr.event_type, pr.pattern_name, pr.id, pr.occurrences, pr.confidence_score, pr.status, "
        "ps.source_outcome_ids, ps.win_rate, ps.bias_accuracy, ps.liquidity_accuracy, ps.false_signal_rate, ps.narrative_accuracy "
        "FROM pattern.pattern_registry pr "
        "JOIN pattern.pattern_statistics ps ON ps.pattern_id = pr.id "
        "WHERE LOWER(pr.event_type) = LOWER('" + event_type + "') LIMIT 1"
    )
    patterns = pg_query_values(pat_sql, pat_cols)
    pattern = patterns[0] if patterns else None
    if not pattern:
        return None

    pb_cols = ['playbook_name','playbook_id','status','maturity_level','occurrences','confidence_score']
    pb_sql = (
        "SELECT playbook_name, id, status, maturity_level, occurrences, confidence_score "
        "FROM playbook.playbook_registry "
        "WHERE LOWER(playbook_name) = LOWER('" + event_type + "_pattern Experimental Playbook') LIMIT 1"
    )
    playbooks = pg_query_values(pb_sql, pb_cols)
    playbook = playbooks[0] if playbooks else None

    ctx = {
        'event_type': event_type,
        'market_context': market_context,
        'pattern_id': pattern['pattern_id'],
        'pattern_name': pattern['pattern_name'],
        'playbook_id': playbook['playbook_id'] if playbook else None,
        'playbook_name': playbook['playbook_name'] if playbook else None,
        'occurrences': int(pattern['occurrences'] or 0),
        'confidence_score': float(pattern['confidence_score'] or 0),
        'maturity_level': 'experimental',
        'evidence_status': 'linked' if pattern.get('source_outcome_ids') else 'empty',
        'source_outcome_ids': pattern.get('source_outcome_ids') or [],
        'governance_warnings': ['Experimental — do not use for direct trading', 'Candidate maturity cap = 70']
    }
    if playbook:
        ctx['maturity_level'] = playbook['maturity_level'] or 'experimental'
    return ctx


def score_context(ctx):
    if ctx is None:
        return {'raw_score': 0, 'maturity_cap': 70, 'final_score': 0, 'components': {}}
    pat_conf = float(ctx.get('confidence_score') or 0)
    play_mat = 40 if ctx['maturity_level'] == 'experimental' else (70 if ctx['maturity_level'] == 'validated' else 80)
    ev_qual = 50 if ctx['evidence_status'] == 'linked' else 20
    out_val = 60 if ctx['occurrences'] >= 2 else 30
    gov_safe = 70 if ctx['governance_warnings'] else 40
    smc = 50
    raw = (pat_conf * 0.25) + (play_mat * 0.20) + (ev_qual * 0.20) + (out_val * 0.15) + (gov_safe * 0.10) + (smc * 0.10)
    maturity_cap = 70 if ctx['maturity_level'] == 'experimental' else (85 if ctx['maturity_level'] == 'published' else 95)
    final = min(raw, maturity_cap)
    return {
        'raw_score': round(raw, 2),
        'maturity_cap': maturity_cap,
        'final_score': round(final, 2),
        'components': {
            'pattern_confidence': pat_conf,
            'playbook_maturity': play_mat,
            'evidence_quality': ev_qual,
            'outcome_validation': out_val,
            'governance_safety': gov_safe,
            'smc_readiness': smc
        }
    }


def recommend(score_obj):
    final = score_obj['final_score'] if score_obj else 0
    if final <= 40:
        return 'WAIT'
    if final <= 60:
        return 'OBSERVE'
    if final <= 75:
        return 'PREPARE'
    if final <= 85:
        return 'REDUCE_RISK'
    return 'INVALIDATE'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--event-type', required=False)
    parser.add_argument('--run-tests', action='store_true')
    args = parser.parse_args()

    if args.run_tests:
        for et in ['cpi', 'fomc', 'nfp']:
            print('TEST ' + et)
            ctx = run_context(et)
            if ctx is None:
                print('  CONTEXT: NONE => WAIT')
                continue
            scores = score_context(ctx)
            rec = recommend(scores)
            print('  CONTEXT: ' + et + ' -> ' + ctx['pattern_name'] + ' / ' + ctx['playbook_name'])
            print('  SCORE: ' + str(scores['final_score']) + ' cap=' + str(scores['maturity_cap']))
            print('  REC: ' + rec)
        raise SystemExit(0)

    ctx = run_context(args.event_type)
    scores = score_context(ctx)
    rec = recommend(scores)
    out = {
        'context': {
            'event_type': ctx.get('event_type') if ctx else None,
            'pattern_name': ctx.get('pattern_name') if ctx else None,
            'playbook_name': ctx.get('playbook_name') if ctx else None,
            'maturity_level': ctx.get('maturity_level') if ctx else None,
            'confidence_score': ctx.get('confidence_score') if ctx else None,
            'evidence_status': ctx.get('evidence_status') if ctx else None,
            'source_outcome_ids': ctx.get('source_outcome_ids') if ctx else [],
            'governance_warnings': ctx.get('governance_warnings') if ctx else [],
        },
        'recommendation': rec,
        'scores': scores,
    }
    print(json.dumps(out, indent=2))
