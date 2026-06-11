# KNOWLEDGE_OS_BRIDGE_RESULT

**Date:** 2026-06-11 15:18:27 UTC
**Status:** PASS

## Evidence

| Gate | Status |
|---|---|
| Host DB reachable | PASS |
| Hermes container DB reachable | PASS |
| Read test (5 tables) | PASS |
| Write test (INSERT + SELECT) | PASS |
| UI/Agent knowledge test | PASS |
| Persistence verified | PASS |
| Security scan clean | PASS |

## Architecture

```
Hermes Agent Container
  -> psycopg2-binary (uv)
  -> TCP 5432
  -> knowledge-os-postgres
  -> knowledge_os database
  -> 5 registry tables
  -> 7 seed records + 1 bridge test record
```

## Commit

Reports committed to thamajakk-cyber/decode-capital-os
