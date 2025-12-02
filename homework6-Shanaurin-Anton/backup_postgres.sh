#!/usr/bin/env bash
set -euo pipefail

# ПАРАМЕТРЫ ПОДКЛЮЧЕНИЯ (можно вынести в .env и делать: source .env)
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-postgres}"  # можно использовать конкретную БД
PGPASSWORD="${PGPASSWORD:-postgres}"  # ЛУЧШЕ передавать извне, не хранить в скрипте

BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"

# Создадим директорию, если её нет
mkdir -p "$BACKUP_DIR"

# Текущая дата во имя файла
DATE="$(date +'%Y-%m-%d_%H-%M-%S')"
BACKUP_FILE="${BACKUP_DIR}/pg_${PGDATABASE}_${DATE}.sql.gz"

export PGPASSWORD

echo "Начинаю резервное копирование PostgreSQL базы '${PGDATABASE}'..."
pg_dump \
  --host="$PGHOST" \
  --port="$PGPORT" \
  --username="$PGUSER" \
  --format=plain \
  --dbname="$PGDATABASE" \
  | gzip > "$BACKUP_FILE"

echo "Бэкап PostgreSQL сохранён: $BACKUP_FILE"

# chmod +x backup_postgres.sh
# PGHOST=postgres PGUSER=postgres PGPASSWORD=secret PGDATABASE=mydb BACKUP_DIR=/backups/postgres ./backup_postgres.sh