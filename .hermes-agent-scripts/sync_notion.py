import os, sys, json, pathlib
import requests

# Load Notion token from standard env files
token = None
for p in ['/root/.hermes/.env', '/opt/data/secrets/notion.env']:
    path = pathlib.Path(p)
    if path.exists():
        for raw in path.read_text(errors='ignore').splitlines():
            line = raw.strip()
            if line.startswith('NOTION_API_KEY='):
                token = line.split('=', 1)[1].strip()
                break
        if token:
            break
if not token:
    sys.exit('MISSING_NOTION_API_KEY')

session = requests.Session()
session.headers.update({
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
})

parent_page_id = '37c3138a-e0c4-80fd-a1ea-dd6c8c43ebc7'

db_specs = {
    'SMC Contexts': {
        'properties': {
            'Name': {'title': {}},
            'Event Type': {'rich_text': {}},
            'Maturity': {'select': {'options': [{'name': 'experimental'}, {'name': 'observed'}, {'name': 'validated'}]}},
            'Evidence': {'url': {}},
        }
    },
    'Market Structure': {
        'properties': {
            'Name': {'title': {}},
            'Structure Type': {'rich_text': {}},
            'Direction': {'select': {'options': [{'name': 'bullish'}, {'name': 'bearish'}, {'name': 'range'}]}},
            'Status': {'select': {'options': [{'name': 'active'}, {'name': 'invalidated'}]}},
        }
    },
    'Liquidity Registry': {
        'properties': {
            'Name': {'title': {}},
            'Liquidity Type': {'rich_text': {}},
            'Swept': {'checkbox': True},
            'Status': {'select': {'options': [{'name': 'active'}, {'name': 'swept'}]}},
        }
    },
    'Decision Overlay': {
        'properties': {
            'Name': {'title': {}},
            'Event Type': {'rich_text': {}},
            'Outcome ID': {'rich_text': {}},
            'Status': {'select': {'options': [{'name': 'experimental'}, {'name': 'observed'}, {'name': 'validated'}]}},
        }
    },
}

# Phase 9A
r = session.get(f'https://api.notion.com/v1/pages/{parent_page_id}')
print('PHASE_9A', r.status_code, r.json().get('object'))

# Phase 9B
created = {}
for name, spec in db_specs.items():
    payload = {
        'parent': {'page_id': parent_page_id},
        'title': [{'type': 'text', 'text': {'content': name}}],
        'properties': spec['properties'],
    }
    resp = session.post('https://api.notion.com/v1/databases', json=payload)
    data = resp.json()
    created[name] = data.get('id')
    print(f'PHASE_9B_CREATE {name}: {resp.status_code} {data.get("id")}')

print('CREATED_IDS', json.dumps(created, ensure_ascii=False))
