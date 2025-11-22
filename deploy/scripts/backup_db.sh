#!/usr/bin/env bash
set -euo pipefail

# Simple pg_dump backup from inside the db container
# Usage: ./deploy/scripts/backup_db.sh [container_name] [backup_dir]

CONTAINER_NAME=${1:-odoo19-prod-db}
BACKUP_DIR=${2:-$(pwd)/backups}

# Load environment for DB credentials if available
if [ -f "$(pwd)/.env" ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source "$(pwd)/.env"
  set +o allexport
fi

POSTGRES_USER=${POSTGRES_USER:-odoo}
POSTGRES_DB=${POSTGRES_DB:-odoo}

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.dump"

echo "Running pg_dump from container $CONTAINER_NAME..."
docker exec -t "$CONTAINER_NAME" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_FILE"

echo "Backup stored at $BACKUP_FILE"
