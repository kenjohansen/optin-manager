#!/bin/bash
# Bulletproof dev runner for OptIn Manager
# Kills all existing backend/frontend dev processes, then launches fresh backend and frontend

set -e

# Kill all previous backend/frontend processes
./kill-all.sh

# Start backend
cd backend
if [ ! -f ../.venv/bin/activate ] && [ -f requirements.txt ]; then
    echo "[run-dev] Creating Python virtualenv..."
    python3 -m venv ../.venv
    source ../.venv/bin/activate
    pip install -r requirements.txt
else
    source ../.venv/bin/activate
fi

echo "[run-dev] Launching backend (uvicorn)..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
if [ ! -d node_modules ]; then
    echo "[run-dev] Installing frontend dependencies..."
    npm install
fi

echo "[run-dev] Launching frontend (npm run dev)..."
npm run dev &
FRONTEND_PID=$!
cd ..

echo "[run-dev] Backend PID: $BACKEND_PID"
echo "[run-dev] Frontend PID: $FRONTEND_PID"
echo "[run-dev] Both backend and frontend are running. Use ./kill-all.sh to stop all dev processes."

wait
