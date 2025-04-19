#!/bin/bash
# Bulletproof DB migration script for OptIn Manager
# Usage: ./scripts/upgrade_db.sh

set -e

cd "$(dirname "$0")/.."

if [ -f alembic.ini ]; then
    echo "[INFO] Running Alembic migrations..."
    alembic upgrade head
else
    echo "[ERROR] Alembic is not set up. Please run: alembic init alembic"
    exit 1
fi
