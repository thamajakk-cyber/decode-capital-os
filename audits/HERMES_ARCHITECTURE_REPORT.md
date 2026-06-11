# HERMES ARCHITECTURE REPORT

**Project:** CAPTAIN MOD SMC PRO MAX — decode-capital-os
**Date:** 2026-06-11T12:09:06Z
**Source:** https://github.com/outsourc-e/hermes-workspace
**Status:** ✅ ARCHITECTURE MAPPED — DO NOT INSTALL (per mission directive)

---

## Overview

Hermes Workspace v2.3.0 is a native web workspace for Hermes Agent — a command center for AI agent orchestration. MIT licensed, 5.6k stars, JavaScript/TypeScript codebase.

---

## Architecture Map

### Services

| Service         | Port  | Description                              |
|-----------------|-------|------------------------------------------|
| Hermes Agent    | 8642  | Core AI agent (API server mode)          |
| Hermes Workspace| 3000  | Web UI (Next.js frontend)                |
| Dashboard       | 9119  | Session/metrics aggregation API          |

### Technology Stack

- **Frontend:** JavaScript (75.2%) + TypeScript (24.3%)
- **Runtime:** Node.js 22+
- **Package Manager:** pnpm
- **Build:** Next.js dev mode or Docker
- **Real-time:** SSE streaming for chat

### Docker Images

| Image                              | Registry  |
|------------------------------------|-----------|
| nousresearch/hermes-agent:latest   | Docker Hub|
| ghcr.io/outsourc-e/hermes-workspace:latest | GHCR |

### Docker Compose (Full Stack)

```
hermes-agent:latest     → port 8642 (API server)
hermes-workspace:latest → port 3000 (Web UI)
```

### Networks

- Default Docker Compose bridge network
- Services communicate via internal Docker DNS

### Volumes

- Persistent session storage (state.db, JSONL transcripts)
- Skills directory (~/.hermes/skills/)
- Memory store (~/.hermes/ for built-in, or external provider)

### Environment Variables

**Required:**
```
HERMES_API_URL=http://127.0.0.1:8642
HERMES_DASHBOARD_URL=http://127.0.0.1:9119
```

**Optional:**
```
HERMES_API_TOKEN=***
HERMES_PASSWORD=***
API_SERVER_ENABLED=true
API_SERVER_HOST=0.0.0.0
API_SERVER_KEY=<auth key>
COOKIE_SECURE=1|0
TRUST_PROXY=1
```

### Reverse Proxy

- Not built-in; recommended: nginx/Caddy/Tailscale for remote access
- TRUST_PROXY=1 for behind-proxy setups

### Authentication

- Auth middleware on all routes
- CSP headers + path-traversal prevention
- HttpOnly + SameSite=Strict cookies
- HERMES_PASSWORD required for non-loopback binding

### AI Providers

Hermes Agent supports 20+ providers (same as this Hermes instance):
OpenRouter, Anthropic, OpenAI, Google Gemini, DeepSeek, xAI, Nous Portal, etc.

Local model support: Ollama via direct connection or gateway proxy.

### Telegram Integration

- Runs through Hermes Agent gateway (already configured on this system)
- Workspace connects to gateway API, not directly to Telegram
- Gateway runs as systemd user service (confirmed active)

### Persistent Storage

| Path                          | Content                    |
|-------------------------------|----------------------------|
| ~/.hermes/config.yaml         | Configuration              |
| ~/.hermes/.env                | Secrets and tokens         |
| ~/.hermes/state.db            | Session store (SQLite)     |
| ~/.hermes/sessions/           | Transcript JSONL files     |
| ~/.hermes/skills/             | Installed skills           |
| ~/.hermes/hermes-agent/       | Source code (if git clone) |

---

## Installation Methods (DO NOT EXECUTE)

### Method 1: One-Line Install
```bash
curl -fsSL https://raw.githubusercontent.com/outsourc-e/hermes-workspace/main/install.sh | bash
```

### Method 2: Attach to Existing Agent
```bash
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace && pnpm install
cp .env.example .env
echo 'HERMES_API_URL=http://127.0.0.1:8642' >> .env
echo 'HERMES_DASHBOARD_URL=http://127.0.0.1:9119' >> .env
pnpm dev
```

### Method 3: Docker Compose
```bash
docker compose up
```

### Method 4: Manual
```bash
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace && pnpm install && pnpm dev
```

---

## Key Dependencies on THIS System

| Dependency       | Status    | Version    |
|------------------|-----------|------------|
| Node.js          | ✅ OK     | v22.22.3   |
| npm              | ✅ OK     | v10.9.8    |
| pnpm             | ❌ MISSING| Not installed|
| Docker           | ❓ UNKNOWN| Need to check |
| Hermes Agent     | ✅ OK     | Active     |
| Telegram Gateway | ✅ OK     | Active     |

---

## Compatibility Assessment

Hermes Agent is already running and configured on this system with:
- Model: mimo-v2.5 via xiaomi provider
- Gateway: systemd user service, Telegram connected
- Tools: hermes-cli toolset enabled

The workspace would connect to the existing gateway at port 8642.
The workspace requires pnpm to be installed first.
