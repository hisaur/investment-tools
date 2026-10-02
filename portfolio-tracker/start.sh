#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================================="
echo "  🚀 GHOSTFOLIO EPHEMERAL PIPELINE: 1-COMMAND RUNNER "
echo "================================================================="

# 1. Ephemeral Secret Configuration (Stable default fallbacks)
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"ghostfolio_ephemeral_pw"}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-"ghostfolio_ephemeral_jwt_secret_1234567890"}
export ACCESS_TOKEN_SALT=${ACCESS_TOKEN_SALT:-"ghostfolio_ephemeral_salt"}

if [ ! -f "$DIR/.env" ] && [ -f "$DIR/.env.example" ]; then
    cp "$DIR/.env.example" "$DIR/.env"
fi

# 2. Stage local CSV
CSV_PATH="${LOCAL_CSV_PATH:-}"
if [ -z "$CSV_PATH" ] && [ -f "$DIR/.env" ]; then
    CSV_PATH=$(grep -E '^\s*LOCAL_CSV_PATH\s*=' "$DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d ' ')
fi
if [ -z "$CSV_PATH" ]; then
    CSV_PATH="$HOME/GoogleDrive/portfolio_docker_sync.csv"
fi

mkdir -p "$DIR/data"
if [ -f "$CSV_PATH" ]; then
    cp "$CSV_PATH" "$DIR/data/portfolio_docker_sync.csv"
    echo "[OK] Synced CSV staged to $DIR/data/portfolio_docker_sync.csv"
fi

echo "[1/4] Starting ephemeral services (PostgreSQL, Redis, Ghostfolio)..."
docker compose -f "$DIR/docker-compose.yml" up -d postgres redis ghostfolio

echo "[2/4] Waiting for Ghostfolio healthcheck..."
retries=0
until curl -s -f http://localhost:3333/api/v1/health > /dev/null || [ $retries -ge 60 ]; do
    echo -n "."
    sleep 1
    retries=$((retries+1))
done
echo ""

if [ $retries -ge 60 ]; then
    echo "[ERROR] Ghostfolio failed to respond healthy within 60 seconds."
    exit 1
fi
echo "[OK] Ghostfolio is ready!"

echo "[3/4] Ingesting portfolio trades..."
if python3 -c "import requests, dateutil" 2>/dev/null; then
    echo "[FAST PATH] Executing native host sync (sub-second direct execution)..."
    GHOSTFOLIO_URL="http://localhost:3333" CSV_FILE_PATH="$CSV_PATH" python3 "$DIR/sync-job/sync.py"
else
    echo "[INFO] Running ingestion inside Docker container..."
    docker compose -f "$DIR/docker-compose.yml" run --rm sync-job
fi

echo "[4/4] Opening Ghostfolio dashboard..."
if which xdg-open > /dev/null 2>&1; then
    xdg-open http://localhost:3333
elif which open > /dev/null 2>&1; then
    open http://localhost:3333
fi

echo ""
echo "================================================================="
echo "  ✨ PIPELINE COMPLETE! GHOSTFOLIO IS READY"
echo "  Dashboard: http://localhost:3333"
echo "  To stop and wipe ephemeral containers when finished: ./cleanup.sh"
echo "================================================================="
