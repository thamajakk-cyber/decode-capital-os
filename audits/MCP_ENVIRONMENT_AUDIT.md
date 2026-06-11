# MCP ENVIRONMENT AUDIT

**Date:** 2026-06-11T12:33:08Z
**Status:** ✅ COMPLETE

---

## Evidence

| Component | Status | Version/Detail |
|-----------|--------|----------------|
| Hermes MCP command | ✅ PASS | `hermes mcp list` functional |
| MCP servers configured | ⚠️ EMPTY | No servers in config (pre-configuration) |
| Node.js | ✅ PASS | v22.22.3 |
| npm | ✅ PASS | v10.9.8 |
| npx | ✅ PASS | v10.9.8 |
| pnpm | ❌ MISSING | Not installed |
| MCP Python SDK | ✅ PASS | v1.26.0 |
| Docker | ✅ PASS | Available, images pullable |
| GitHub MCP Docker image | ✅ PASS | ghcr.io/github/github-mcp-server:latest (v1.2.0) |
| Deprecated npm MCP | ⚠️ READY | @modelcontextprotocol/server-github (deprecated but functional) |
| GitHub PAT | ⚠️ LIMITED | Read: ✅ Write: ❌ (403) |

---

## Commands Executed

```
$ hermes mcp list
No MCP servers configured.

$ node --version
v22.22.3

$ npm --version
v10.9.8

$ npx --version
v10.9.8

$ pip show mcp
Name: mcp
Version: 1.26.0

$ docker images | grep github-mcp
ghcr.io/github/github-mcp-server   latest   <size>   <time>
```

---

## .env State (secrets redacted)

- GITHUB_TOKEN: present (read-only capable)
- XIAOMI_API_KEY: present (active)
- All other provider keys: commented out or absent
