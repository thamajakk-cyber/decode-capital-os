# PROVIDER_ROOT_CAUSE_REPORT

**Date:** 2026-06-11 14:18:06 UTC
**Status:** ROOT CAUSE PROVEN

## Root Cause

The "Invalid API key" error was from the GATEWAY authentication layer, NOT from Xiaomi. Gateway has API_SERVER_KEY set; requests without Bearer token are rejected.

## Evidence

- Without auth: "Invalid API key" (gateway rejection)
- With auth: HTTP 200, real mimo-v2.5 response
- Direct Xiaomi API (Anthropic format): HTTP 200
- Anthropic SDK from container: SUCCESS

## Provider Config

- Provider: xiaomi, Model: mimo-v2.5
- Base URL: https://token-plan-sgp.xiaomimimo.com/anthropic
- API mode: anthropic_messages (auto-detected from /anthropic suffix)
- Key: XIAOMI_API_KEY (51 chars, valid)
