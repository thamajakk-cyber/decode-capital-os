# CORE_TABLES_PERFORMANCE_REPORT

**Date:** 2026-06-11 15:08:10 UTC

## Database Metrics

| Metric | Value |
|---|---|
| DB Size | 8MB |
| Tables | 5 |
| Indexes | 24 |
| Records | 7 |

## Query Performance

Knowledge tag search: 0.038ms execution time
Seq scan (appropriate for small dataset — will switch to index scan as data grows)

## Index Coverage

All primary keys indexed (B-tree).
GIN index on knowledge.tags (array search).
B-tree indexes on all foreign keys and frequently queried columns.

## Connection Health

max_connections: 100
Active: ~6
WAL level: replica (backup ready)
