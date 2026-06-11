# INSTALLATION READINESS GATE

**Project:** CAPTAIN MOD SMC PRO MAX — decode-capital-os
**Date:** 2026-06-11T12:09:06Z
**Mode:** RCAF — Root Cause, Fix, Verify, Retry
**Evidence Standard:** NO EVIDENCE = FAIL

---

## Readiness Assessment

### Q1: Is GitHub configured correctly?

**Status: ❌ FAIL**

| Sub-check                 | Status    | Evidence                              |
|---------------------------|-----------|---------------------------------------|
| Git installed             | ✅ PASS   | v2.43.0                               |
| Git identity set          | ❌ FAIL   | No .gitconfig, no user.name/email     |
| GitHub auth configured    | ❌ FAIL   | No PAT, no SSH key, no gh CLI        |
| Push capability           | ❌ FAIL   | Untestable without auth               |
| Pull capability           | ❌ FAIL   | Untestable without auth               |

**Root Cause:** Fresh system with no prior GitHub configuration.
**Evidence:** Empty ~/.gitconfig, empty ~/.ssh/, no tokens in env or .env.

---

### Q2: Is MCP operational?

**Status: ❌ FAIL**

| Sub-check                 | Status    | Evidence                              |
|---------------------------|-----------|---------------------------------------|
| MCP SDK installed         | ✅ PASS   | mcp v1.26.0                           |
| Hermes MCP client ready   | ✅ PASS   | Built-in, functional                  |
| Servers configured        | ❌ FAIL   | mcp_servers section empty in config   |
| GitHub MCP server ready   | ⚠️ READY  | npx package available (deprecated)    |
| GitHub PAT for MCP        | ❌ FAIL   | No token available                    |
| Connection tested         | ❌ FAIL   | Cannot test without server+token      |

**Root Cause:** MCP infrastructure exists but no server is configured. No GitHub token available for authentication.
**Evidence:** `hermes mcp list` returns "No MCP servers configured."

---

### Q3: Is Version Control verified?

**Status: ❌ FAIL**

| Sub-check                 | Status    | Evidence                              |
|---------------------------|-----------|---------------------------------------|
| Git functional            | ✅ PASS   | v2.43.0                               |
| Local repo initialized    | ❌ FAIL   | git init not run                      |
| Remote configured         | ❌ FAIL   | No .git, no remote                    |
| Commit history exists     | ❌ FAIL   | No commits                            |
| Branch workflow tested    | ❌ FAIL   | Untestable                            |

**Root Cause:** Repository not yet initialized. No git identity to create commits.
**Evidence:** /root/decode-capital-os/ exists but has no .git directory.

---

### Q4: Is Rollback possible?

**Status: ❌ FAIL**

| Sub-check                 | Status    | Evidence                              |
|---------------------------|-----------|---------------------------------------|
| Git history exists        | ❌ FAIL   | No commits to roll back to            |
| Remote backup exists      | ❌ FAIL   | No remote repository                  |
| Checkpoint system active  | ⚠️ N/A   | Hermes checkpoints, not git-based     |

**Root Cause:** No version history exists yet.
**Evidence:** No .git directory, no commits, no remote.

---

### Q5: Is Audit Trail available?

**Status: ❌ FAIL**

| Sub-check                 | Status    | Evidence                              |
|---------------------------|-----------|---------------------------------------|
| Git log functional        | ❌ FAIL   | No commits to log                     |
| Audit reports generated   | ✅ PASS   | This document + siblings exist        |
| Evidence artifacts        | ✅ PASS   | /evidence/ directory created           |
| Persistent logging        | ⚠️ PARTIAL| Hermes session DB tracks activity     |

**Root Cause:** No git commits = no version-control audit trail.
**Evidence:** These audit reports exist but are not yet version-controlled.

---

### Q6: Is Backup strategy available?

**Status: ❌ FAIL**

| Sub-check                 | Status    | Evidence                              |
|---------------------------|-----------|---------------------------------------|
| Remote repo as backup     | ❌ FAIL   | No remote configured                  |
| Automated backups         | ❌ FAIL   | No backup cron/script configured      |
| Local snapshot            | ⚠️ PARTIAL| Files exist locally only              |

**Root Cause:** No remote repository exists to back up to. No backup automation.
**Evidence:** Files are local-only, single point of failure.

---

### Q7: Is Hermes architecture understood?

**Status: ✅ PASS**

| Sub-check                 | Status    | Evidence                              |
|---------------------------|-----------|---------------------------------------|
| Architecture mapped       | ✅ PASS   | HERMES_ARCHITECTURE_REPORT.md         |
| Services identified       | ✅ PASS   | Agent (8642), Workspace (3000), Dashboard (9119) |
| Dependencies known        | ✅ PASS   | Node.js ✅, pnpm ❌, Docker ❓        |
| Installation paths known  | ✅ PASS   | 4 methods documented                  |
| Config requirements known | ✅ PASS   | Env vars, auth, proxy all mapped      |

**Evidence:** Complete architecture report generated from repo analysis.

---

## Summary

| Question                              | Status  |
|---------------------------------------|---------|
| 1. GitHub configured correctly?       | ❌ FAIL |
| 2. MCP operational?                   | ❌ FAIL |
| 3. Version Control verified?          | ❌ FAIL |
| 4. Rollback possible?                 | ❌ FAIL |
| 5. Audit Trail available?             | ❌ FAIL |
| 6. Backup strategy available?         | ❌ FAIL |
| 7. Hermes architecture understood?    | ✅ PASS |

**BLOCKED items: 6/7**

---

## Required Actions (Priority Order)

### P0 — Unblocking (Must complete before anything else)

1. **Generate GitHub Personal Access Token**
   - Go to: https://github.com/settings/tokens
   - Generate classic token with scopes: repo, read:org, workflow
   - Expiration: 90 days recommended

2. **Configure Git Identity**
   ```bash
   git config --global user.name "<NAME>"
   git config --global user.email "<EMAIL>"
   ```

3. **Set GitHub Token**
   - Add to ~/.hermes/.env: GITHUB_TOKEN=<token>
   - Or configure SSH key authentication

4. **Verify Repository Access**
   ```bash
   gh auth status  # or git ls-remote
   ```

### P1 — Post-Auth

5. Create/Verify decode-capital-os Repository
6. Initialize Local Git Repository
7. Configure MCP GitHub Server
8. Run Full Workflow Validation

### P2 — Readiness

9. Install pnpm (needed for hermes-workspace)
10. Verify Docker (optional, for containerized install)
