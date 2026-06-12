import requests
import json
import sys
from pathlib import Path

# Load token
token = None
for p in ['/root/.hermes/.env', '/opt/data/secrets/notion.env']:
    path = Path(p)
    if path.exists():
        with open(path, 'r', errors='ignore') as f:
            for raw in f:
                line = raw.strip()
                if line.startswith('NOTION_API_KEY='):
                    token = line.split('=', 1)[1].strip()
                    break
        if token:
            break
if not token:
    sys.exit('MISSING_NOTION_API_KEY')

headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}
parent_page_id = '37c3138a-e0c4-80fd-a1ea-dd6c8c43ebc7'


db_configs = [
    {
        'key': 'smc_contexts_id',
        'title': 'SMC Contexts',
        'properties': {
            'Name': {'title': {}},
            'Event Type': {'rich_text': {}},
            'Maturity': {'select': {'options': [{'name': 'experimental'}, {'name': 'observed'}, {'name': 'validated'}]}},
            'Evidence': {'url': {}},
        }
    },
    {
        'key': 'market_structure_id',
        'title': 'Market Structure',
        'properties': {
            'Name': {'title': {}},
            'Structure Type': {'rich_text': {}},
            'Direction': {'select': {'options': [{'name': 'bullish'}, {'name': 'bearish'}, {'name': 'range'}]}},
            'Status': {'select': {'options': [{'name': 'active'}, {'name': 'invalidated'}]}}
        }
    },
    {
        'key': 'liquidity_registry_id',
        'title': 'Liquidity Registry',
        'properties': {
            'Name': {'title': {}},
            'Liquidity Type': {'rich_text': {}},
            'Swept': {'checkbox': True},
            'Status': {'select': {'options': [{'name': 'active'}, {'name': 'swept'}]}}
        }
    },
    {
        'key': 'decision_overlay_id',
        'title': 'Decision Overlay',
        'properties': {
            'Name': {'title': {}},
            'Event Type': {'rich_text': {}},
            'Outcome ID': {'rich_text': {}},
            'Status': {'select': {'options': [{'name': 'experimental'}, {'name': 'observed'}, {'name': 'validated'}]}}
        }
    }
]

created = {}
session = requests.Session()
session.headers.update(headers)
for cfg in db_configs:
    payload = {
        'parent': {'page_id': parent_page_id},
        'title': [{'type': 'text', 'text': {'content': cfg['title']}}],
        'properties': cfg['properties'],
    }
    resp = session.post('https://api.notion.com/v1/databases', json=payload)
    resp.raise_for_status()
    data = resp.json()
    created[cfg['key']] = data.get('id')
    print(f"{cfg['title']}: status={resp.status_code} id={data.get('id')}")

print(json.dumps({'created_databases': created}, indent=2))
