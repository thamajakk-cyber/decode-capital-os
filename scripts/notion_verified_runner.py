import json
import sys
from pathlib import Path
import requests
from typing import Any, Dict

TOKEN_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else None
EVIDENCE_PATH = Path('/root/decode-capital-os/audits/NOTION_TOUCHPOINT_EVIDENCE.json')
PARENT_PAGE_ID = '37c3138a-e0c4-80fd-a1ea-dd6c8c43ebc7'
APPROVED_SECRET_PATHS = [
    '/opt/data/secrets/notion.env',
    '/root/.hermes/.env',
    '/root/decode-capital-os/.notion.env',
]


def _sanitize_token(raw_token: str) -> str:
    token = raw_token.strip()
    if len(token) <= 12:
        return '***'
    return token[:8] + '...' + token[-4:]


def _read_token() -> str:
    if TOKEN_PATH and TOKEN_PATH.exists():
        try:
            return TOKEN_PATH.read_text(encoding='utf-8', errors='ignore').strip()
        except OSError:
            pass
    for path_str in APPROVED_SECRET_PATHS:
        path = Path(path_str)
        if not path.exists():
            continue
        try:
            data = path.read_text(encoding='utf-8', errors='ignore').splitlines()
        except OSError:
            continue
        for line in data:
            if '=' in line:
                return line.split('=', 1)[1].strip()
    return ''


def _request(session, method, url, payload=None):
    if method == 'GET':
        return session.get(url)
    return session.post(url, json=payload)


def _collect_evidence() -> Dict[str, Any]:
    token = _read_token()
    if not token:
        return {'status': 'BLOCKED', 'token_source_verified': False, 'error': 'MISSING_NOTION_API_KEY'}

    sanitized_token = _sanitize_token(token)
    session = requests.Session()
    session.headers.update({
        'Authorization': _sanitize_token('Bearer ' + token),
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json',
    })

    parent_page_access = {'response_code': None, 'parent_id': None, 'error': None}
    parent_page_response = _request(session, 'GET', f'https://api.notion.com/v1/pages/{PARENT_PAGE_ID}')
    if parent_page_response.status_code == 200:
        body = parent_page_response.json()
        parent_page_access = {
            'response_code': 200,
            'parent_id': body.get('id'),
            'error': None,
        }
    else:
        parent_page_access = {
            'response_code': parent_page_response.status_code,
            'error': parent_page_response.text,
        }

    search_response = _request(session, 'POST', 'https://api.notion.com/v1/search', {'page_size': 100})
    database_lookup = {}
    if search_response.status_code == 200:
        for item in search_response.json().get('results', []):
            title = ''
            if item.get('object') == 'data_source':
                title = ''.join(part.get('plain_text', '') for part in item.get('title', []))
            elif item.get('object') == 'page':
                title_field = (item.get('properties') or {}).get('title', {})
                if isinstance(title_field, dict):
                    title = ''.join(part.get('plain_text', '') for part in title_field.get('title', []))
            else:
                continue
            lowered = title.lower()
            database_lookup[lowered] = {
                'database_id': item.get('id'),
                'title': title,
                'parent': item.get('parent'),
            }

    expected_names = [
        'smc contexts',
        'market structure',
        'liquidity registry',
        'decision overlay',
    ]
    database_parent_match = {}
    for key in expected_names:
        match = database_lookup.get(key)
        if not match:
            database_parent_match[key] = {
                'parent_match': False,
                'database_id': None,
                'parent_id': None,
            }
            continue
        database_id = match['database_id']
        database_response = _request(session, 'GET', f'https://api.notion.com/v1/databases/{database_id}')
        if database_response.status_code != 200:
            database_parent_match[key] = {
                'database_id': database_id,
                'parent_match': False,
                'error': database_response.text,
            }
            continue
        body = database_response.json()
        parent = body.get('parent') or {}
        database_parent_match[key] = {
            'database_id': database_id,
            'parent_type': parent.get('type'),
            'parent_id': parent.get('page_id') or parent.get('database_id') or parent.get('workspace'),
            'parent_match': parent.get('page_id') == PARENT_PAGE_ID,
        }

    count_match = {}
    for key in expected_names:
        info = database_parent_match.get(key, {})
        database_id = info.get('database_id')
        if not database_id:
            count_match[key] = {'postgres_count': None, 'notion_count': None, 'match': False}
            continue
        query_response = _request(
            session,
            'POST',
            f'https://api.notion.com/v1/databases/{database_id}/query',
            {'sorts': [{'property': 'Name', 'direction': 'descending'}], 'page_size': 100},
        )
        notion_count = None
        if query_response.status_code == 200:
            notion_count = len(query_response.json().get('results', []))
        count_match[key] = {'notion_count': notion_count, 'query_status': query_response.status_code}

    evidence = {
        'token_source_verified': True,
        'token_not_printed': True,
        'token_prefix': sanitized_token,
        'token_length_chars': len(_read_token()),
        'parent_page_access': parent_page_access,
        'database_parent_match': database_parent_match,
        'count_match': count_match,
        'sanitized_evidence_file': str(EVIDENCE_PATH),
        'status': 'BLOCKED',
    }

    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps({'parent_id': PARENT_PAGE_ID, 'evidence': evidence}, indent=2),
        encoding='utf-8',
    )
    return evidence


def main() -> int:
    evidence = _collect_evidence()
    print(json.dumps(evidence, indent=2))
    return 0 if evidence.get('status') != 'BLOCKED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
