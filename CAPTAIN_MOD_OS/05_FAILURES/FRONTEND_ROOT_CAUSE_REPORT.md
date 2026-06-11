# FRONTEND_ROOT_CAUSE_REPORT

**Date:** 2026-06-11 14:18:06 UTC
**Status:** ROOT CAUSE PROVEN

## Root Cause

Dashboard s6 run script defaults HERMES_DASHBOARD_HOST to 127.0.0.1 inside agent container. Workspace container connects via Docker DNS (hermes-agent:9119) which cannot reach loopback. Result: workspace /api/sessions returns 500, frontend crashes on .map() over undefined.

## Evidence

- Dashboard from agent (127.0.0.1:9119): HTTP 200
- Dashboard from workspace (hermes-agent:9119): HTTP 000 (connection refused)
- s6 container_environment had HERMES_DASHBOARD_HOST=127.0.0.1

## Fix

Added HERMES_DASHBOARD_HOST=0.0.0.0 and HERMES_DASHBOARD_INSECURE=1 to .env file.
Also removed --insecure from compose command (unsupported by this hermes version).
