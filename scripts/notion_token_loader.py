import sys
from pathlib import Path

class TokenLoader:
    PATHS=***    '/opt/data/secrets/notion.env',
        '/root/.hermes/.env',
        '/root/decode-capital-os/.notion.env',
    ]

    def load(self):
        for raw_path in self.PATHS:
            path = Path(raw_path)
            if not path.exists():
                continue
            try:
                lines = path.read_text(errors='ignore').splitlines()
            except Exception:
                continue
            for line in lines:
                if line.startswith('NOTION_API_KEY=***                    token=line.split('=',1)[1].strip()
                    return token
        return ''
