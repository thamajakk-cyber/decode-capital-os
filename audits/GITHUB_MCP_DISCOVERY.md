# GITHUB MCP SERVER DISCOVERY

**Date:** 2026-06-11T12:33:08Z
**Status:** ✅ COMPLETE

---

## Options Evaluated

### Option 1: Official GitHub MCP Server (Docker) — SELECTED
- **Repo:** github/github-mcp-server (30.6k stars, MIT)
- **Version:** v1.2.0 (June 8, 2026)
- **Image:** ghcr.io/github/github-mcp-server:latest
- **Transport:** Docker stdio
- **Auth:** GITHUB_PERSONAL_ACCESS_TOKEN env var
- **Toolsets:** 19 categories, 41 tools
- **Status:** ✅ Downloaded, tested, working

### Option 2: Deprecated npm Package
- **Package:** @modelcontextprotocol/server-github
- **Status:** ⚠️ Deprecated but functional
- **Transport:** npx stdio
- **Note:** Not recommended for production

### Option 3: Remote GitHub-hosted
- **URL:** https://api.githubcopilot.com/mcp/
- **Auth:** OAuth
- **Note:** Requires MCP host with HTTP transport support

---

## Selected: Docker (Official)

### Capabilities (41 tools discovered)

**Context:** get_me
**Repos:** get_file_contents, create_or_update_file, create_branch, push_files, delete_file, fork_repository, search_code, list_branches, list_commits, list_tags, get_commit, get_tag, get_latest_release, get_release_by_tag, list_releases, list_repository_collaborators, get_teams, get_team_members
**Issues:** issue_read, issue_write, list_issues, search_issues, add_issue_comment, list_issue_types, sub_issue_write
**Pull Requests:** pull_request_read, pull_request_review_write, create_pull_request, update_pull_request, merge_pull_request, list_pull_requests, search_pull_requests, add_comment_to_pending_review, add_reply_to_pull_request_comment, update_pull_request_branch
**Users:** search_users
**Actions:** (via repos toolset)
**Code Security:** (available via toolset config)

### Authentication

- **Method:** GITHUB_PERSONAL_ACCESS_TOKEN env var
- **Current PAT capabilities:** READ ✅ WRITE ❌
- **PAT limitation:** Fine-grained token lacks Contents write permission

### Security

- Token passed via env var (not CLI arg)
- Hermes MCP client filters env vars for stdio servers
- Credential redaction active in error messages
- No tokens committed to repository

---

## Configuration Target

```yaml
mcp_servers:
  github:
    command: "docker"
    args: ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
           "-e", "GITHUB_TOOLSETS=context,repos,issues,pull_requests,users",
           "ghcr.io/github/github-mcp-server:latest"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "<from .env>"
    timeout: 120
    connect_timeout: 60
```
