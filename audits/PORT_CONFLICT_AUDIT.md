# PORT CONFLICT AUDIT

**Date:** 2026-06-11T12:55:50Z
**Host:** srv1437654

---

## Currently Occupied Ports

| Port | Process | Binding | Risk |
|------|---------|---------|------|
| 22 | sshd | 0.0.0.0 | None (standard) |
| 53 | systemd-resolved | 127.0.0.53 | None (loopback) |
| 65529 | monarx-agent | 127.0.0.1 | None (loopback) |

---

## Hermes Workspace Target Ports

| Port | Service | Status |
|------|---------|--------|
| 3000 | hermes-workspace | FREE |
| 5432 | PostgreSQL | FREE (not needed) |
| 8080 | (alt) | FREE |
| 8642 | hermes-agent | FREE |
| 9119 | hermes-dashboard | FREE |

**All 5 target ports are available. No conflicts.**

---

## Reverse Proxy

| Server | Status |
|--------|--------|
| nginx | NOT installed |
| caddy | NOT installed |
| apache2 | NOT installed |

**No reverse proxy installed.** Required for decodecapital.tech HTTPS.

---

## Docker

| Check | Status |
|-------|--------|
| Running containers | NONE |
| Existing volumes | NONE |
| Docker networks | Default only |

**Docker is clean and unused.**

---

## Publicly Exposed Ports

Only port 22 (SSH) is publicly exposed.
All other services bind to 127.0.0.1 (loopback only).

---

## Recommendation

For decodecapital.tech deployment:
1. Install nginx or caddy as reverse proxy
2. Proxy pass 443 -> 127.0.0.1:3000 (hermes-workspace)
3. Workspace and Agent stay on loopback (never public)
