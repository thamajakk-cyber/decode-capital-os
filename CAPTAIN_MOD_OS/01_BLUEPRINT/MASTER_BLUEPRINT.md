---
type: blueprint
project: Captain Mod OS
version: 1.0.0
created: 2026-06-11
---

# 🗺️ Master Blueprint — Captain Mod OS

## Vision

Captain Mod OS is a **repeatable, auditable, recoverable, version-controlled** operating system for AI-driven decision making, knowledge management, and operational intelligence.

## Architecture

```
┌─────────────────────────────────────────────┐
│              CAPTAIN MOD OS                  │
├─────────────┬───────────────┬───────────────┤
│  Obsidian   │  PostgreSQL   │    Hermes     │
│   Vault     │  Knowledge OS │   Workspace   │
│ (Structure) │  (Storage)    │  (Execution)  │
├─────────────┴───────────────┴───────────────┤
│              GitHub Foundation               │
│         (Version Control + Audit Trail)      │
└─────────────────────────────────────────────┘
```

## Core Principles

1. **Evidence First** — No claim without proof
2. **RCAF Loop** — Root Cause → Fix → Verify → Retry
3. **No Fake Passes** — Real hashes, real outputs, real verification
4. **Secrets Isolation** — `/opt/data/secrets/` only
5. **Source of Truth** — PostgreSQL for data, Obsidian for structure, GitHub for history

## Stack

| Layer | Technology | Purpose |
|---|---|---|
| Execution | Hermes Agent | AI agent workspace |
| Storage | PostgreSQL 17.10 | Structured knowledge storage |
| Interface | Obsidian Vault | Human-readable knowledge structure |
| Versioning | GitHub (SSH) | Code and document version control |
| Inference | Xiaomi mimo-v2.5 | Primary AI provider |
| Communication | Telegram | User interface |
| Proxy | nginx 1.24.0 | SSL termination, routing |
| Container | Docker 29.5.3 | Service orchestration |

## Domain Schemas

| Schema | Registry Table | Obsidian Folder |
|---|---|---|
| `knowledge` | `knowledge_registry` | `02_KNOWLEDGE` |
| `decision` | `decision_registry` | `04_DECISIONS` |
| `failure` | `failure_registry` | `05_FAILURES` |
| `lesson` | `lesson_registry` | `03_LESSONS` |
| `agent` | `agent_memory_registry` | `09_AGENTS` |
| `research` | (future tables) | `06_RESEARCH` |
| `project` | (future tables) | `07_PROJECTS` |
| `audit` | (future tables) | `audits/` |

## Phases Completed

1. ✅ Infrastructure (VPS, DNS, SSL, nginx)
2. ✅ GitHub Foundation (SSH, repo, MCP)
3. ✅ Hermes Workspace (Docker, agent, UI)
4. ✅ Provider Layer (Xiaomi mimo-v2.5)
5. ✅ Telegram Integration
6. ✅ Security (secrets, auth)
7. ✅ PostgreSQL Knowledge OS
8. ✅ Core Tables Foundation
9. ✅ Hermes ↔ PostgreSQL Bridge
10. ✅ Obsidian Vault Foundation

## Phases Remaining

11. Obsidian ↔ PostgreSQL Automation (NOT yet — awaiting approval)
12. Notion Integration (NOT yet — awaiting approval)
13. Knowledge Population
14. Operational Runbooks
