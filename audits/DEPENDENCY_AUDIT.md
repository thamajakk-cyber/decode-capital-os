# DEPENDENCY AUDIT

**Date:** 2026-06-11T12:55:50Z
**Host:** Linux srv1437654 6.8.0-124-generic x86_64
**OS:** Ubuntu 24.04.4 LTS

---

## System Resources

| Resource | Value | Required | Status |
|----------|-------|----------|--------|
| CPU | 2 cores | 2+ | PASS |
| RAM | 7.8GB (6.9GB available) | 4GB+ | PASS |
| Disk | 96GB (89GB free) | 20GB+ | PASS |
| OS | Ubuntu 24.04 LTS | Linux | PASS |
| Kernel | 6.8.0-124-generic | 5.x+ | PASS |

---

## Software Dependencies

| Software | Version | Required | Status |
|----------|---------|----------|--------|
| Docker | 29.5.3 | 20+ | PASS |
| Docker Compose | 5.1.4 | 2.0+ | PASS |
| Node.js | 22.22.3 | 22.0+ | PASS |
| npm | 10.9.8 | 8+ | PASS |
| pnpm | NOT INSTALLED | Needed for manual | BLOCKED (for manual only) |
| Python | 3.11.15 | 3.8+ | PASS |
| Git | 2.43.0 | 2.x | PASS |

---

## Authentication

| Service | Status | Evidence |
|---------|--------|----------|
| GitHub SSH | PASS | thamajakk-cyber authenticated |
| GitHub MCP | PASS | 41 tools, read/write verified |
| GitHub PAT | PASS | Classic token, repo scope |

---

## Database

| Component | Required | Status |
|-----------|----------|--------|
| PostgreSQL | Optional (not in compose) | NOT NEEDED |
| SQLite | Built into Hermes Agent | PASS (bundled) |

---

## Network

| Check | Status |
|-------|--------|
| Internet access | PASS (HTTP 200 to GitHub) |
| DNS resolution | PASS |
| Outbound HTTPS | PASS |

---

## Missing (for manual install only)

| Item | Action Required |
|------|-----------------|
| pnpm | npm install -g pnpm |

**Docker Compose path requires NO additional software.**
