# INSTALLATION PLAN

**Date:** 2026-06-11T12:56:46Z
**Target:** decodecapital.tech -> Hermes Workspace
**Method:** Docker Compose
**Server:** 76.13.220.27

---

## Prerequisites (Before Installation)

### Step 0.1: DNS Configuration
```
Action: Add A record for decodecapital.tech -> 76.13.220.27
Action: Add A record for www.decodecapital.tech -> 76.13.220.27
Platform: Hostinger DNS panel
TTL: 300 (5 minutes)
Verification: dig decodecapital.tech A +short == 76.13.220.27
```

### Step 0.2: Secret Directory Setup
```bash
mkdir -p /opt/data/secrets
chmod 700 /opt/data/secrets
```

### Step 0.3: Create Secret Files
```
/opt/data/secrets/github.env     -> GITHUB_TOKEN
/opt/data/secrets/mcp.env        -> GITHUB_PERSONAL_ACCESS_TOKEN
/opt/data/secrets/telegram.env   -> TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS
/opt/data/secrets/providers.env  -> XIAOMI_API_KEY (or other provider keys)
/opt/data/secrets/workspace.env  -> HERMES_PASSWORD, API_SERVER_KEY
```

### Step 0.4: Install Reverse Proxy
```bash
apt update && apt install -y nginx certbot python3-certbot-nginx
```

---

## Installation Steps

### Step 1: Clone Repository
```bash
cd /opt
git clone git@github.com:outsourc-e/hermes-workspace.git
cd hermes-workspace
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```

Edit .env with production values:
```
HERMES_API_URL=http://hermes-agent:8642
HERMES_API_TOKEN=<from /opt/data/secrets/workspace.env>
HERMES_PASSWORD=<strong password>
COOKIE_SECURE=true
TRUST_PROXY=1
XIAOMI_API_KEY=<from /opt/data/secrets/providers.env>
```

### Step 3: Docker Compose Configuration
Ensure docker-compose.yml mounts secrets:
```yaml
volumes:
  - /opt/data:/opt/data
  - hermes-agent-data:/home/workspace/.hermes
  - /opt/data/secrets/github.env:/etc/secrets/github.env:ro
  - /opt/data/secrets/telegram.env:/etc/secrets/telegram.env:ro
  - /opt/data/secrets/providers.env:/etc/secrets/providers.env:ro
```

### Step 4: Pull and Start
```bash
docker compose pull
docker compose up -d
```

### Step 5: Verify Health
```bash
# Wait 60s for startup
sleep 60

# Check containers
docker compose ps

# Check health endpoints
curl -s http://127.0.0.1:8642/health
curl -s http://127.0.0.1:9119/api/status
curl -s http://127.0.0.1:3000/
```

### Step 6: Configure Reverse Proxy
```nginx
# /etc/nginx/sites-available/decodecapital.tech
server {
    listen 80;
    server_name decodecapital.tech www.decodecapital.tech;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name decodecapital.tech www.decodecapital.tech;

    ssl_certificate /etc/letsencrypt/live/decodecapital.tech/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/decodecapital.tech/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### Step 7: SSL Certificate
```bash
ln -s /etc/nginx/sites-available/decodecapital.tech /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
certbot --nginx -d decodecapital.tech -d www.decodecapital.tech
```

### Step 8: Final Verification
```bash
curl -sI https://decodecapital.tech
# Should return 200 with HSTS header
```

---

## Rollback Steps

```bash
# Stop everything
cd /opt/hermes-workspace
docker compose down

# Restore previous version (if upgraded)
git checkout <previous-tag>
docker compose up -d

# Or full cleanup
docker compose down -v  # removes volumes too
rm -rf /opt/hermes-workspace
```

---

## Verification Checklist

| Step | Verification | Command |
|------|-------------|---------|
| DNS | A record resolves | dig decodecapital.tech A +short |
| Secrets | Files exist with correct perms | ls -la /opt/data/secrets/ |
| Docker | Containers running | docker compose ps |
| Health | Agent healthy | curl localhost:8642/health |
| Health | Workspace healthy | curl localhost:3000 |
| SSL | HTTPS works | curl -sI https://decodecapital.tech |
| Reverse Proxy | Nginx running | systemctl status nginx |
