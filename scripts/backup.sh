#!/usr/bin/env bash
set -euo pipefail

date_tag=$(date +%F_%H-%M-%S)
mkdir -p /tmp/newlife-backups/$date_tag

docker exec $(docker ps -qf name=postgres) pg_dump -U postgres newlife > /tmp/newlife-backups/$date_tag/postgres.sql
docker exec $(docker ps -qf name=clickhouse) clickhouse-client --query "BACKUP DATABASE default TO Disk('backups', 'ch_$date_tag')"
docker exec $(docker ps -qf name=redis) redis-cli BGSAVE

echo "Backups completed: /tmp/newlife-backups/$date_tag"
