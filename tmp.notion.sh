set -e
TOKEN_FILE=$(mktemp)
grep '^NOTION_API_KEY=*** /opt/data/secrets/notion.env | cut -d= -f2- > "$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"
python3 - <<'PYEOF'
import requests, json, sys
from pathlib import Path
token = Path('/tmp/notion_tmp_token').read_text().strip()
