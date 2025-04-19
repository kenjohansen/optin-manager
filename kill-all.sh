#!/bin/bash
# Kill all backend and frontend dev processes for OptIn Manager

# Kill by port (backend:8000, frontend:5173)
lsof -ti:8000 | xargs -r kill
lsof -ti:5173 | xargs -r kill

# Kill uvicorn (backend), python (backend), node/npm (frontend) processes
pkill -f 'uvicorn app.main:app' 2>/dev/null
pkill -f 'python.*app.main' 2>/dev/null
pkill -f 'npm run dev' 2>/dev/null
pkill -f 'node.*vite' 2>/dev/null

# Print status
echo "Killed all OptIn Manager backend (uvicorn/python) and frontend (npm/node) dev processes."
