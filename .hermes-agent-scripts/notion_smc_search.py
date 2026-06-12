
import os, json, pathlib, subprocess

def load_token():
    for p in ['/root/.hermes/.env', '/opt/data/secrets/notion.env']:
        f = pathlib.Path(p)
        if f.exists():
            for line in f.read_text().splitlines():
                if line.startswith('NOTION_API_KEY=***                    return line.split('=', 1)[1].strip()
    raise SystemExit('NOTION_API_KEY not found')

token = load_token()
authtoken = 'Authorization: Bearer ' + token
base = ['curl', '-s', '-H', authtoken, '-H', 'Notion-Version: 2025-09-03', '-H', 'Content-Type: application/json']

def notion_json(path, method='GET', data=None):
    cmd = base + ['-X', method, 'https://api.notion.com/' + path]
    if data is not None:
        cmd += ['-d', json.dumps(data)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        print('RAW', out[:200])
        raise

results = notion_json('v1/search?page_size=100').get('results', [])
print('SEARCH_COUNT', len(results))
for item in results:
    o = item.get('object')
    iid = item.get('id')
    typ = item.get('type')
    title = ''
    props = item.get('properties', {}) or {}
    for key in ['title', 'Name']:
        if key in props and props[key]:
            title = ''.join(x.get('plain_text', '') for x in props[key])
            break
    if o in ('page', 'data_source', 'database'):
        print(o + '\t' + iid + '\t' + str(typ) + '\t' + title)
print('SEARCH_DONE')
