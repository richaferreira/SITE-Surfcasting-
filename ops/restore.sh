#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Uso: $0 backups/AAAAMMDDTHHMMSSZ" >&2
  exit 2
fi

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
BACKUP_DIR="$1"
MYSQL_DATABASE="${MYSQL_DATABASE:-surfcasting}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-root_dev_only}"

for file in manifest.txt SHA256SUMS mysql.sql.gz neo4j.dump uploads.tar.gz; do
  test -f "${BACKUP_DIR}/${file}" || { echo "Arquivo ausente: ${file}" >&2; exit 3; }
done

(
  cd "${BACKUP_DIR}"
  sha256sum -c SHA256SUMS
)

echo "[restore] interrompendo aplicações"
docker compose -f "${COMPOSE_FILE}" stop frontend backend >/dev/null 2>&1 || true

echo "[restore] restaurando MySQL"
gunzip -c "${BACKUP_DIR}/mysql.sql.gz" | docker compose -f "${COMPOSE_FILE}" exec -T mysql \
  mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" "${MYSQL_DATABASE}"

echo "[restore] restaurando Neo4j"
docker compose -f "${COMPOSE_FILE}" stop neo4j >/dev/null
docker compose -f "${COMPOSE_FILE}" run --rm --no-deps \
  --entrypoint neo4j-admin neo4j \
  database load neo4j --from-path=/backups/"$(basename "${BACKUP_DIR}")" --overwrite-destination=true

echo "[restore] restaurando mídia"
rm -rf uploads
mkdir -p uploads
tar -xzf "${BACKUP_DIR}/uploads.tar.gz"

echo "[restore] reiniciando stack"
docker compose -f "${COMPOSE_FILE}" up -d neo4j backend frontend

echo "[restore] validando readiness"
for attempt in $(seq 1 30); do
  if curl --fail --silent http://localhost:8000/health/ready >/dev/null 2>&1; then
    echo "[restore] restauração concluída e validada"
    exit 0
  fi
  sleep 2
done

echo "Readiness não ficou verde após restauração." >&2
exit 4
