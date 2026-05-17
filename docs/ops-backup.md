# Backup & Recovery Policy

## PostgreSQL
- Full backup: daily (`pg_basebackup` / `pg_dump` depending on size)
- WAL archiving enabled
- Retention: 30 days

## ClickHouse
- Snapshot backups daily
- Retention: 30 days

## Redis
- RDB snapshots + AOF where low RPO required
- Retention: 30 days

## Restore Drill
- Quarterly restoration test in staging
- Checklist: DB integrity, API smoke, login flow, media links, task reports
