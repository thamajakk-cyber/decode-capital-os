# FRONTEND_PROVIDER_FREEZE_STATE

**Date:** 2026-06-11 14:18:06 UTC
**Status:** Pre-fix state captured

## Container Status

| Container | Image | Status | Ports |
|---|---|---|---|
| hermes-workspace-hermes-agent-1 | nousresearch/hermes-agent:latest | Up (healthy) | 127.0.0.1:8642 |
| hermes-workspace-hermes-workspace-1 | ghcr.io/outsourc-e/hermes-workspace:latest | Up (healthy) | 127.0.0.1:3000 |

## Known Issues (Pre-fix)

1. Frontend: "Cannot read properties of undefined (reading 'map')" in sessions
2. Provider: "Invalid API key" from gateway auth layer (NOT Xiaomi)
3. Dashboard binding: 127.0.0.1 only, unreachable from workspace container
4. Gateway command: --insecure flag not recognized in this version
