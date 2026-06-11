# HERMES REPOSITORY DISCOVERY

**Date:** 2026-06-11T12:55:50Z
**Repository:** https://github.com/outsourc-e/hermes-workspace
**Version:** 2.3.0 | **License:** MIT | **Node.js:** >=22.0.0
**Status:** Architecture fully mapped

---

## Services

### Service 1: hermes-agent (Gateway + Dashboard)
- **Image:** nousresearch/hermes-agent:latest
- **Command:** ["gateway", "run"]
- **Ports:**
  - 8642 -> Gateway API (bound to 127.0.0.1)
  - 9119 -> Dashboard (internal only, Docker network)
- **Health Check:** http://localhost:8642/health + http://localhost:9119/api/status
  - interval: 10s, timeout: 5s, retries: 5, start_period: 30s
- **Env Vars:** API_SERVER_HOST=0.0.0.0, API_SERVER_ENABLED=true, API_SERVER_KEY

### Service 2: hermes-workspace (Web UI)
- **Image:** ghcr.io/outsourc-e/hermes-workspace:latest
- **Depends On:** hermes-agent (condition: healthy)
- **Ports:** 127.0.0.1:3000:3000
- **Env Vars:**
  - HERMES_API_URL=http://hermes-agent:8642
  - HERMES_API_TOKEN=${API_SERVER_KEY}
  - HERMES_PASSWORD (REQUIRED for remote)
  - COOKIE_SECURE (true for HTTPS)
  - TRUST_PROXY

---

## Ports Summary

| Port | Service | Binding | Purpose |
|------|---------|---------|---------|
| 3000 | hermes-workspace | 127.0.0.1 | Web UI (SSR + static) |
| 8642 | hermes-agent | 127.0.0.1 | Gateway API |
| 9119 | hermes-agent | internal only | Dashboard API |

**All ports bound to 127.0.0.1** (not exposed to public internet directly).

---

## Volumes

1. **hermes-agent-data**
   - Mounts: /opt/data (agent) + /home/workspace/.hermes (workspace, rw)
   - Contents: Agent config, sessions, skills, memory, credentials

2. **hermes-workspace-files**
   - Mounts: /workspace (workspace container)
   - Contents: Files from workspace file browser

---

## Environment Variables (Complete)

**LLM Provider Keys:**
- ANTHROPIC_API_KEY, NOUS_API_KEY, OPENAI_API_KEY
- OPENROUTER_API_KEY, GOOGLE_API_KEY, MINIMAX_API_KEY

**Connection:**
- HERMES_API_URL (default: http://127.0.0.1:8642)
- HERMES_API_TOKEN, HERMES_AGENT_PATH
- HERMES_DASHBOARD_URL (default: http://127.0.0.1:9119)

**Security:**
- HOST (default: 127.0.0.1)
- HERMES_PASSWORD / CLAUDE_PASSWORD (REQUIRED for remote)
- COOKIE_SECURE (1/0), TRUST_PROXY (1/0)
- API_SERVER_KEY

**Server:**
- PORT (default: 3000), NODE_ENV
- STREAM_ACCEPTED_TIMEOUT_MS (120000)
- STREAM_HANDOFF_TIMEOUT_MS (300000)

---

## Dockerfile (Multi-stage)

**Build Stage:**
- Base: node:22-slim
- Corepack enabled, pnpm install --frozen-lockfile, pnpm build

**Runtime Stage:**
- Base: node:22-slim
- Adds: tini, ca-certificates, curl, python3
- Creates workspace user (uid=10010)
- Copies gosu from tianon/gosu:1.17-bookworm
- Drop root via gosu to workspace user
- CMD: node --max-old-space-size=2048 server-entry.js

---

## Network

- Docker default bridge network
- Internal service-to-service via Docker DNS
- Workspace -> Agent: http://hermes-agent:8642

---

## Key Dependencies (package.json)

React 19.2, TanStack Start, Vite 7.3.2, Three.js, Monaco Editor,
xterm 5.3.0, Zustand, Framer Motion, Playwright 1.58.2,
Recharts 3.7, TypeScript 5.7.2, ESLint 10, Vitest 3.0.5
