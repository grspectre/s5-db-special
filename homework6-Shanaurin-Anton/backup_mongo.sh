#!/usr/bin/env bash
set -euo pipefail

MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_USER="${MONGO_USER:-}"
MONGO_PASSWORD="${MONGO_PASSWORD:-}"
MONGO_DB="${MONGO_DB:-}"    # если пусто — дамп всех БД

BACKUP_DIR="${BACKUP_DIR:-/backups/mongo}"

mkdir -p "$BACKUP_DIR"

DATE="$(date +'%Y-%m-%d_%H-%M-%S')"
BACKUP_PATH="${BACKUP_DIR}/mongo_${DATE}"

AUTH_PARAMS=()
if [[ -n "$MONGO_USER" && -n "$MONGO_PASSWORD" ]]; then
  AUTH_PARAMS+=( -u "$MONGO_USER" -p "$MONGO_PASSWORD" --authenticationDatabase "admin" )
fi

DB_PARAM=()
if [[ -n "$MONGO_DB" ]]; then
  DB_PARAM+=( --db "$MONGO_DB" )
fi

echo "Начинаю резервное копирование MongoDB..."
mongodump \
  --host="$MONGO_HOST" \
  --port="$MONGO_PORT" \
  "${AUTH_PARAMS[@]}" \
  "${DB_PARAM[@]}" \
  --out="$BACKUP_PATH"

echo "Бэкап MongoDB сохранён: $BACKUP_PATH"

# chmod +x backup_mongo.sh
# MONGO_HOST=mongo BACKUP_DIR=/backups/mongo ./backup_mongo.sh