# BACKUP AND RECOVERY REPORT

**Date:** 2026-06-11T12:56:46Z
**Status:** Strategy defined, not yet implemented

---

## Current State

| Component | Backup Exists | Evidence |
|-----------|--------------|----------|
| /opt/data/secrets | N/A | Directory does not exist yet |
| ~/.hermes/.env | NO | No backup strategy |
| ~/.hermes/config.yaml | NO | No backup strategy |
| ~/.hermes/state.db | NO | No backup strategy |
| Git repository | YES | thamajakk-cyber/decode-capital-os |
| Docker volumes | N/A | No containers yet |

---

## Planned Volume Strategy

### hermes-agent-data Volume
- **Mount:** /opt/data
- **Contents:** Agent config, sessions, skills, memory
- **Backup method:** Docker volume snapshot + rsync
- **Frequency:** Daily

### hermes-workspace-files Volume
- **Mount:** /workspace
- **Contents:** User files from file browser
- **Backup method:** Docker volume snapshot + rsync
- **Frequency:** Daily

---

## Rollback Capability

| Scenario | Rollback Method | Difficulty |
|----------|----------------|------------|
| Bad deploy | docker compose down + up (previous image) | EASY |
| Config error | Restore config.yaml from git | EASY |
| Corrupted DB | Restore state.db from backup | MEDIUM |
| Bad upgrade | docker compose down, pull previous tag, up | EASY |
| Full disaster | Reinstall from scratch + restore volumes | MEDIUM |

---

## Disaster Recovery

**Recovery time objective (RTO):** 30 minutes
**Recovery point objective (RPO):** 24 hours (daily backups)

**Recovery steps:**
1. Clone decode-capital-os repo (has configs + docs)
2. Pull Docker images
3. Restore volume backups to /opt/data
4. docker compose up -d
5. Verify health checks pass
6. Update DNS if needed

---

## Secret Management Strategy

**Target directory:** /opt/data/secrets/

| File | Contents |
|------|----------|
| github.env | GITHUB_TOKEN, GITHUB_PERSONAL_ACCESS_TOKEN |
| mcp.env | MCP-related tokens |
| telegram.env | TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS |
| providers.env | LLM provider API keys |
| workspace.env | HERMES_PASSWORD, API_SERVER_KEY, COOKIE settings |

**Security:**
- chmod 700 /opt/data/secrets/
- chmod 600 /opt/data/secrets/*.env
- Never commit to git
- Never mount into Docker image layers
- Mount as Docker secrets or bind-mount individual files
