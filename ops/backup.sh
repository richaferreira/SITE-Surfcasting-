#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="${BACKUP_DIR:-backups}/${STAMP}"
MYSQL_DATABASE="${MYSQL_DATABASE:-surfcasting}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-root_dev_only}"

mkdir -p "${BACKUP_DIR}"

echo "[backup] MySQL -> ${BACKUP_DIR}/mysql.sql.gz"
docker compose -f "${COMPOSE_FILE}" exec -T mysql \
  mysqldump -uroot -p"${MYSQL_ROOT_PASSWORD}" \
  --single-transaction --routines --triggers --events --hex-blob "${MYSQL_DATABASE}" \
  | gzip -9 > "${BACKUP_DIR}/mysql.sql.gz"

echo "[backup] Neo4j -> dump consistente"
docker compose -f "${COMPOSE_FILE}" stop neo4j >/dev/null
docker compose -f "${COMPOSE_FILE}" run --rm --no-deps \
  --entrypoint neo4j-admin neo4j \
  database dump neo4j --to-path=/backups/"${STAMP}" --overwrite-destination=true

docker compose -f "${COMPOSE_FILE}" up -d neo4j >/dev/null

echo "[backup] mídia -> ${BACKUP_DIR}/uploads.tar.gz"
if [ -d uploads ]; then
  tar -czf "${BACKUP_DIR}/uploads.tar.gz" uploads
else
  tar -czf "${BACKUP_DIR}/uploads.tar.gz" --files-from /dev/null
fi

cat > "${BACKUP_DIR}/manifest.txt" <<EOF
created_at=${STAMP}
mysql_database=${MYSQL_DATABASE}
mysql=mysql.sql.gz
neo4j=neo4j.dump
media=uploads.tar.gz
EOF

sha256sum "${BACKUP_DIR}"/* > "${BACKUP_DIR}/SHA256SUMS"
echo "[backup] concluído: ${BACKUP_DIR}"
