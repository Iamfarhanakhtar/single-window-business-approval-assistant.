#!/bin/bash
# SIH-130 Unified Business Compliance Hub Starter
# Starts FastAPI Backend (port 8000) and Next.js Frontend (port 3000)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================================"
echo " Starting Business Compliance Hub (SIH Problem 130)"
echo "========================================================"

# Free ports 3000 & 8000 if occupied
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start FastAPI Backend in background
echo "[1/2] Launching FastAPI Backend on http://localhost:8000..."
(cd "$ROOT_DIR/backend" && .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &
BACKEND_PID=$!

# Trap Ctrl+C to kill backend when frontend exits
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill -9 $BACKEND_PID 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Give backend a moment to initialize
sleep 2

# Start Next.js Frontend
echo "[2/2] Launching Next.js Frontend on http://localhost:3000..."
cd "$ROOT_DIR/frontend"
npx next dev -p 3000
