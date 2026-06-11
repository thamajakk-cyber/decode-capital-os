# MCP CONNECTION REPORT

**Project:** CAPTAIN MOD SMC PRO MAX — decode-capital-os
**Date:** 2026-06-11T12:09:06Z
**Status:** ❌ NOT OPERATIONAL — Prerequisites met but no server configured

---

## MCP Infrastructure Status

| Component               | Status    | Evidence                              |
|-------------------------|-----------|---------------------------------------|
| MCP Python SDK          | ✅ PASS   | v1.26.0 installed                     |
| Node.js (npx servers)   | ✅ PASS   | v22.22.3                              |
| npm                     | ✅ PASS   | v10.9.8                               |
| npx                     | ✅ PASS   | v10.9.8                               |
| Hermes MCP client       | ✅ PASS   | Built-in, functional                  |
| MCP config in Hermes    | ⚠️ EMPTY  | No servers under mcp_servers key      |
| GitHub MCP server       | ⚠️ READY  | Available but not configured          |
| GitHub PAT for MCP      | ❌ BLOCKED| No token available                    |

---

## Supported MCP Servers for GitHub

### Option 1: Official GitHub MCP Server (Docker — Recommended)
- **Repo:** github/github-mcp-server (30.6k stars, MIT)
- **Latest:** v1.2.0 (June 8, 2026)
- **Transport:** Docker stdio
- **Auth:** GITHUB_PERSONAL_ACCESS_TOKEN env var
- **Toolsets:** 18 categories (repos, issues, PRs, actions, code_security, etc.)
- **Requires:** Docker + PAT

### Option 2: Deprecated npm Package
- **Package:** @modelcontextprotocol/server-github
- **Status:** ⚠️ DEPRECATED (but functional)
- **Transport:** npx stdio
- **Auth:** GITHUB_PERSONAL_ACCESS_TOKEN env var
- **Requires:** PAT only

### Option 3: Remote (GitHub-hosted)
- **URL:** https://api.githubcopilot.com/mcp/
- **Auth:** Via MCP host (VS Code, Claude Desktop)
- **Note:** Requires MCP host supporting HTTP transport

---

## Target MCP Configuration

```yaml
# ~/.hermes/config.yaml mcp_servers section
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "<PAT_HERE>"
    timeout: 60
```

Or Docker variant:
```yaml
mcp_servers:
  github:
    command: "docker"
    args: ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "<PAT_HERE>"
    timeout: 120
```

---

## Authentication Requirements

**PAT Scopes Required:**
- repo — Full repository access (read/write)
- read:org — Organization visibility
- workflow — GitHub Actions access (optional)

**Security Requirements:**
- Token stored in ~/.hermes/.env (not in config.yaml)
- Environment variable filtering in Hermes MCP client prevents token leakage
- Credential redaction in error messages active (security.redact_secrets: true)

---

## Connection Test Plan (Pending Auth)

```
1. hermes mcp add github --command npx --args "-y @modelcontextprotocol/server-github"
   Set GITHUB_PERSONAL_ACCESS_TOKEN in env config
2. hermes mcp test github
   Expected: Connection successful, tools discovered
3. In-session: call mcp_github_list_issues or similar
   Expected: Returns data from authenticated GitHub account
```

---

## Blockers

1. **No GitHub PAT** — Cannot authenticate to any MCP server variant
2. **No Docker** (optional) — Docker variant preferred but npx variant works
3. **pnpm not installed** — Needed for hermes-workspace build, not for MCP
