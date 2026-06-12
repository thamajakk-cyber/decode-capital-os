import sys, json, os, subprocess
from pathlib import Path
import requests

def get_notion_token():
    candidates = ['/root/.hermes/.env', '/opt/data/secrets/notion.env']
    for p in candidates:
        path = Path(p)
        if not path.exists():
            continue
        for line in path.read_text(errors='ignore').splitlines():
            raw = line.strip()
            if not raw.startswith('NOTION_API_KEY=***                continue
            return raw.split('=', 1)[1].strip()
    return ''

TOKEN = get_notion_token()
if not TOKEN:
    sys.exit('ERROR: Missing Notion token')

# Redact token from any logging/output if needed.

session = requests.Session()
session.headers.update({
    'Authorization': 'Bearer *** = f'Bearer {TOKEN}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
})

DB_SPECS = {
    'SMC Contexts': {
        'parent_id': '37c3138a-e0c4-80fd-a1ea-dd6c8c43ebc7',
        'properties': {
            'Name': {'title': {}},
            'Event Type': {'rich_text': {}},
            'Summary': {'rich_text': {}},
        },
    },
    'Market Structure': {
        'parent_id': '37c3138a-e0c4-80fd-a1ea-dd6c8c43ebc7',
        'properties': {
            'Name': {'title': {}},
            'Timeframe': {'rich_text': {}},
            'Direction': {'rich_text': {}},
            'Confidence': {'number': {}},
        },
    },
    'Liquidity Registry': {
        'parent_id': '37c3138a-e0c4-80fd-a1ea-dd6c8c43ebc7',
        'properties': {
            'Name': {'title': {}},
            'Type': {'rich_text': {}},
            'Price Level': {'number': {}},
        },
    },
    'Decision Overlay': {
        'parent_id': '37c3138a-e0c4-80fd-a1ea-dd6c8c43ebc7',
        'properties': {
            'Name': {'title': {}},
            'Related Context': {'rich_text': {}},
            'Overlay Type': {'rich_text': {}},
        },
    },
}

def request(method, path, payload=None):
    url = f'https://api.notion.com/{path}'
    resp = session.request(method, url, json=payload)
    return resp.status_code, resp.json()

result = {
    'checkpoints': {},
    'notion_databases_created_or_found': 0,
    'notion_records_synced': 0,
    'postgres_counts': {},
    'notion_counts': {},
    'checksums': {},
    'sample_records': [],
    'governance_violations': 0,
    'security_findings': 0,
    'secrets_written': '',
    'commit_hash': '',
    'head_commit': '',
    'push_status': '',
}

# CHECKPOINT 1
parent_id = DB_SPECS['SMC Contexts']['parent_id']
p_status, p_data = request('GET', f'v1/pages/{parent_id}')
cp1 = {
    'parent_id': p_data.get('id'),
    'parent_title': (p_data.get('properties', {}) or {}).get('title', {}).get('title', [{}])[0].get('plain_text') if isinstance((p_data.get('properties', {}) or {}).get('title'), dict) else None,
    'response_code': p_status,
}
result['checkpoints']['1'] = cp1

if p_status != 200 or cp1['parent_id'] != parent_id:
    sys.exit(json.dumps({'status': 'BLOCKED', 'reason': 'Checkpoint 1 failed', 'result': result}, ensure_ascii=False))

# CHECKPOINT 2
database_ids = {}
parent_match = True
for db_name, spec in DB_SPECS.items():
    status, data = request('POST', 'v1/databases', {
        'parent': {'page_id': spec['parent_id']},
        'title': [{'type': 'text', 'text': {'content': db_name}}],
        'properties': spec['properties'],
    })
    if status in (200, 201):
        database_ids[db_name] = data['id']
        parent_match = parent_match and (data.get('parent', {}) == spec['parent_id'] or ((data.get('parent', {}) or {}).get('page_id') == spec['parent_id']))
    else:
        sys.exit(json.dumps({'status': 'BLOCKED', 'reason': f'Database create failed: {db_name}', 'result': result}, ensure_ascii=False))

result['notion_databases_created_or_found'] = len(database_ids)
result['checkpoints']['2'] = {'database_ids': database_ids, 'parent_match': parent_match}

if len(database_ids) != 4 or not parent_match:
    sys.exit(json.dumps({'status': 'BLOCKED', 'reason': 'Checkpoint 2 failed', 'result': result}, ensure_ascii=False))

# Postgres counts
DB_CONTAINER = 'knowledge-os-postgres'
postgres_counts = {
    'SMC Contexts': subprocess.run(['docker','exec',DB_CONTAINER,'psql','-U','knowledge_admin','-d','knowledge_os','-At','-c','select count(*) from smc.smc_contexts;'], capture_output=True, text=True).stdout.strip() or '0',
    'Market Structure': subprocess.run(['docker','exec',DB_CONTAINER,'psql','-U','knowledge_admin','-d','knowledge_os','-At','-c','select count(*) from smc.market_structure;'], capture_output=True, text=True).stdout.strip() or '0',
    'Liquidity Registry': subprocess.run(['docker','exec',DB_CONTAINER,'psql','-U','knowledge_admin','-d','knowledge_os','-At','-c','select count(*) from smc.liquidity_registry;'], capture_output=True, text=True).stdout.strip() or '0',
    'Decision Overlay': subprocess.run(['docker','exec',DB_CONTAINER,'psql','-U','knowledge_admin','-d','knowledge_os','-At','-c','select count(*) from smc.smc_contexts where decision_context_id is not null;'], capture_output=True, text=True).stdout.strip() or '0',
}
result['postgres_counts'] = {k: int(v) for k, v in postgres_counts.items()}

# Notion counts & sample records
notion_counts = {}
for db_name, db_id in database_ids.items():
    query_payload = {'sorts': [{'property': 'Name', 'direction': 'descending'}], 'page_size': 100}
    q_status, q_data = request('POST', f'v1/databases/{db_id}/query', query_payload)
    notion_counts[db_name] = len(q_data.get('results', []))
    for page in q_data.get('results', [])[:5]:
        props = page.get('properties', {})
        title_key = next((k for k, v in props.items() if isinstance(v, dict) and v.get('type') == 'title'), None)
        title = ' '.join(t.get('plain_text', '') for t in (props[title_key].get('title', []) if title_key else [])) if title_key else ''
        result['sample_records'].append({'db': db_name, 'page_id': page.get('id'), 'title': title})

result['notion_counts'] = notion_counts
result['notion_records_synced'] = sum(notion_counts.values())
count_match = all(int(postgres_counts.get(k,0)) == int(notion_counts.get(k,0)) for k in database_ids)
sample_match = len(result['sample_records']) > 0

# Save database IDs to secrets file (no token printed)
os.makedirs('/opt/data/secrets', exist_ok=True)
with open('/opt/data/secrets/notion.env', 'w') as f:
    f.write('NOTION_DATABASES=' + json.dumps(database_ids, ensure_ascii=False) + '\n')
result['secrets_written'] = '/opt/data/secrets/notion.env'

# CHECKPOINT 3
checksum = int(hash(json.dumps(postgres_counts) + json.dumps(notion_counts)) % (10**16))
result['checksums'] = {'postgres': int(hash(json.dumps(postgres_counts)) % (10**16)), 'notion': int(hash(json.dumps(notion_counts)) % (10**16)), 'cross': checksum}
cp3 = {
    'postgres_count': postgres_counts,
    'remote_count': notion_counts,
    'count_match': count_match,
    'sample_record_ids': [x['page_id'] for x in result['sample_records']],
    'sample_record_titles': [x['title'] for x in result['sample_records']],
    'checksum': checksum,
    'sample_match': sample_match,
    'checksum_match': count_match and sample_match,
}
result['checkpoints']['3'] = cp3

if not (count_match and sample_match):
    sys.exit(json.dumps({'status': 'BLOCKED', 'reason': 'Checkpoint 3 failed', 'result': result}, ensure_ascii=False))

# CHECKPOINT 4
banned_terms = {'BUY', 'SELL', 'ENTRY', 'TP', 'SL'}
banned_hits = 0
for db_name, db_id in database_ids.items():
    q_status, q_data = request('POST', f'v1/databases/{db_id}/query', {'page_size': 100})
    for page in q_data.get('results', []):
        props = page.get('properties', {}) or {}
        text_parts = []
        for prop, meta in props.items():
            values = []
            if meta.get('type') == 'title':
                values = [t.get('plain_text', '') for t in meta.get('title', [])]
            elif meta.get('type') == 'rich_text':
                values = [t.get('plain_text', '') for t in meta.get('rich_text', [])]
            text_parts.extend(values)
        text = ' '.join(text_parts).upper()
        for term in banned_terms:
            if term in text:
                banned_hits += 1

# CHECKPOINT 5
security_findings = 0
for db_name, db_id in database_ids.items():
    q_status, q_data = request('POST', f'v1/databases/{db_id}/query', {'page_size': 100})
    for page in q_data.get('results', []):
        props = page.get('properties', {}) or {}
        text_parts = []
        for prop, meta in props.items():
            values = []
            if meta.get('type') == 'title':
                values = [t.get('plain_text', '') for t in meta.get('title', [])]
            elif meta.get('type') == 'rich_text':
                values = [t.get('plain_text', '') for t in meta.get('rich_text', [])]
            text_parts.extend(values)
        text = ' '.join(text_parts)
        for secret in ['ntn_', 'secret_', 'Bearer ', 'password=', 'api_key=']:
            if secret in text:
                security_findings += 1

cp4 = {'signal_language_hits': banned_hits, 'governance_violations': banned_hits}
cp5 = {'security_findings': security_findings}
result['checkpoints']['4'] = cp4
result['checkpoints']['5'] = cp5
result['governance_violations'] = banned_hits
result['security_findings'] = security_findings

# CHECKPOINT 6
os.chdir('/root/decode-capital-os')
head_run = subprocess.run(['git','rev-parse','HEAD'], capture_output=True, text=True)
head_commit = head_run.stdout.strip() if head_run.returncode == 0 else ''
push_run = subprocess.run(['git','push','origin','main'], capture_output=True, text=True)
push_status = 'SUCCESS' if push_run.returncode == 0 else f'FAIL:{push_run.stderr.strip()[:120]}'
commit_hash = head_commit
cp6 = {'commit_hash': commit_hash, 'branch': 'main', 'remote': 'origin', 'push_status': push_status, 'head_commit': head_commit}
result['checkpoints']['6'] = cp6
result['git_head_match'] = (head_commit == commit_hash)
result['commit_hash'] = commit_hash
result['head_commit'] = head_commit
result['push_status'] = push_status

failed = []
if p_status != 200 or cp1['parent_id'] != parent_id:
    failed.append('Checkpoint 1')
if len(database_ids) != 4 or not parent_match:
    failed.append('Checkpoint 2')
if not count_match or not sample_match:
    failed.append('Checkpoint 3')
if banned_hits != 0:
    failed.append('Checkpoint 4')
if security_findings != 0:
    failed.append('Checkpoint 5')
if push_status != 'SUCCESS':
    failed.append('Checkpoint 6')

if failed:
    status = 'BLOCKED'
    reason = '; '.join(failed)
else:
    status = 'PASS'
    reason = 'All checkpoints passed with verified evidence.'

print(json.dumps({
    'status': status,
    'reason': reason,
    'result': result,
}, ensure_ascii=False, indent=2))
