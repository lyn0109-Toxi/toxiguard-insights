#!/usr/bin/env bash

# ------------------------------------------------------------
# Automatic launch script for LY-Type1 (FastAPI backend)
# ------------------------------------------------------------
# This script
#   1. Ensures a Python virtual environment exists (./.venv)
#   2. Installs required dependencies if not already present
#   3. Starts the FastAPI server (module LY-Type1.harness) in the background
#   4. Writes server logs to logs/ly_type1.log
#   5. Provides a small health‑check (curl) to confirm the service is up.
# ------------------------------------------------------------

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/ly_type1.log"
PYTHON="python3"

# Create logs directory if missing
mkdir -p "$LOG_DIR"

# ------------------------------------------------------------
# Step 1 – create virtual environment if it does not exist
# ------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
  echo "[$(date)] Creating virtual environment at $VENV_DIR" | tee -a "$LOG_FILE"
  $PYTHON -m venv "$VENV_DIR"
fi

# ------------------------------------------------------------
# Step 2 – activate venv and install dependencies
# ------------------------------------------------------------
source "$VENV_DIR/bin/activate"
# Upgrade pip for safety
pip install --upgrade pip >> "$LOG_FILE" 2>&1
# Install requirements – expects a requirements.txt in the project root
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
  echo "[$(date)] Installing Python dependencies" | tee -a "$LOG_FILE"
  pip install -r "$PROJECT_ROOT/requirements.txt" >> "$LOG_FILE" 2>&1
else
  echo "[$(date)] WARNING: requirements.txt not found – you may need to install packages manually" | tee -a "$LOG_FILE"
fi

# ------------------------------------------------------------
# Step 3 – launch FastAPI server in background
# ------------------------------------------------------------
# Use the harness module (python -m ly_type1.harness) which starts uvicorn on 0.0.0.0:8000
# Redirect stdout & stderr to the log file, and store the PID for later stop.
echo "[$(date)] Starting ly_type1 FastAPI server..." | tee -a "$LOG_FILE"
nohup $PYTHON -m ly_type1.harness > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

echo "[$(date)] Server PID: $SERVER_PID" | tee -a "$LOG_FILE"

# ------------------------------------------------------------
# Step 4 – simple health‑check (wait up to 15 seconds for the docs endpoint)
# ------------------------------------------------------------
MAX_WAIT=15
SECONDS_WAITED=0
while [ $SECONDS_WAITED -lt $MAX_WAIT ]; do
  if curl -s http://localhost:8000/docs >/dev/null; then
    echo "[$(date)] FastAPI docs are reachable – server is up" | tee -a "$LOG_FILE"
    break
  fi
  sleep 1
  ((SECONDS_WAITED++))
done
if [ $SECONDS_WAITED -ge $MAX_WAIT ]; then
  echo "[$(date)] ERROR: FastAPI docs not reachable after $MAX_WAIT seconds. Check $LOG_FILE for details." | tee -a "$LOG_FILE"
fi

# ------------------------------------------------------------
# Step 5 – optional helper to stop the server later
# ------------------------------------------------------------
# To stop the server, run:
#   kill $SERVER_PID
#   echo "Server stopped"

# Keep script alive so that the background process isn’t orphaned when the
# terminal closes (optional – comment out if you prefer immediate return).
# read -p "Press ENTER to terminate the server..." dummy
# kill $SERVER_PID
# echo "[$(date)] Server terminated" | tee -a "$LOG_FILE"
