#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

if [ ! -f .env ]; then
  echo ".env file not found. Copy .env.example to .env and fill in the values."
  exit 1
fi

echo "Pulling latest code..."
git pull origin main

echo "Pulling latest images (if any)..."
docker compose -f docker-compose.prod.yml pull

echo "Starting/Updating containers..."
docker compose -f docker-compose.prod.yml up -d

echo "Pruning old resources (optional)"
docker system prune -f

echo "Deployment complete."
