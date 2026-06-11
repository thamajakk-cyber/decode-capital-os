# GITHUB MCP CONFIGURATION REPORT

**Date:** 2026-06-11T12:33:08Z
**Status:** ✅ CONFIGURED (read capability verified, write blocked by PAT)

---

## Configuration Applied

File: ~/.hermes/config.yaml → mcp_servers section

```yaml
mcp_servers:
  github:
    command: "docker"
    args:
      - "run"
      - "-i"
      - "--rm"
      - "-e"
      - "GITHUB_PERSONAL_ACCESS_TOKEN"
      - "-e"
      - "GITHUB_TOOLSETS=context,repos,issues,pull_requests,users"
      - "ghcr.io/github/github-mcp-server:latest"
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "<from .env>"
    timeout: 120
    connect_timeout: 60
```

---

## Security Measures

| Measure | Status |
|---------|--------|
| Token not printed in config | ✅ Referenced from .env |
| Token not committed to repo | ✅ .gitignore blocks .env |
| Token not displayed in reports | ✅ All values redacted |
| Env var filtering active | ✅ Only safe vars passed to Docker |
| Credential redaction active | ✅ security.redact_secrets: true |

---

## Required Capability

| Operation | Capability | Status |
|-----------|-----------|--------|
| List repository | get_me, search_repositories | ✅ Verified |
| Read file | get_file_contents | ✅ Verified |
| Create branch | create_branch | ✅ Available |
| Create/update file | create_or_update_file | ⚠️ PAT lacks permission |
| Verify commit | get_commit | ✅ Available |

---

## PAT Permission Status

**Read operations:** ✅ WORKING
- get_me → authenticated as thamajakk-cyber
- get_file_contents → README.md downloaded (SHA: df3e8ed...)
- get_file_contents → AUDIT file downloaded (SHA: 1d4e2a...)

**Write operations:** ❌ BLOCKED
- create_or_update_file → 403 "Resource not accessible by personal access token"
- Root cause: Fine-grained PAT lacks "Contents: Read and write" permission

---

## To Enable Write Access

1. Go to https://github.com/settings/tokens
2. Edit the current fine-grained token
3. Under "Repository permissions":
   - Set **Contents** to "Read and write"
4. Save changes

**OR** create a Classic token with `repo` scope.
