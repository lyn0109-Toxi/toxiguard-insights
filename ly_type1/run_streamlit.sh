#!/usr/bin/env bash
# run_streamlit.sh – launch LY‑Type1 Streamlit UI

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/ly_type1.log"

# Ensure logs directory exists
mkdir -p "${LOG_DIR}"

# ------------------------------------------------------------
# Step 1 – create / activate virtual environment if missing
# ------------------------------------------------------------
if [ ! -d "${VENV_DIR}" ]; then
  echo "[$(date)] Creating virtual environment…" | tee -a "${LOG_FILE}"
  python3 -m venv "${VENV_DIR}"
fi

# Activate virtualenv
source "${VENV_DIR}/bin/activate"

# ------------------------------------------------------------
# Step 2 – install / upgrade dependencies
# ------------------------------------------------------------
pip install --upgrade pip >> "${LOG_FILE}" 2>&1
if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
  echo "[$(date)] Installing dependencies…" | tee -a "${LOG_FILE}"
  pip install -r "${PROJECT_ROOT}/requirements.txt" >> "${LOG_FILE}" 2>&1
fi

# ------------------------------------------------------------
# Step 3 – launch Streamlit (background) and health‑check
# ------------------------------------------------------------
echo "[$(date)] Starting Streamlit server…" | tee -a "${LOG_FILE}"
nohup streamlit run "${PROJECT_ROOT}/streamlit_app.py" \
  --server.port 8501 \
  --server.headless true \
  > "${LOG_FILE}" 2>&1 &
SERVER_PID=$!
echo "[$(date)] Streamlit PID: $SERVER_PID" | tee -a "${LOG_FILE}"

# Simple health‑check (wait up to 15 s for UI to be reachable)
MAX_WAIT=15
SECONDS_WAITED=0
while [ $SECONDS_WAITED -lt $MAX_WAIT ]; do
  if curl -s http://localhost:8501/_stcore/heartbeat > /dev/null; then
    echo "[$(date)] Streamlit UI is up!" | tee -a "${LOG_FILE}"
    break
  fi
  sleep 1
  ((SECONDS_WAITED++))
done

if [ $SECONDS_WAITED -ge $MAX_WAIT ]; then
  echo "[$(date)] ERROR: Streamlit UI not reachable after $MAX_WAIT s" | tee -a "${LOG_FILE}"
fi

# Optional keep‑alive (comment out if not needed)
# read -p "Press ENTER to stop Streamlit…" dummy
# kill $SERVER_PID
# echo "[$(date)] Streamlit stopped" | tee -a "${LOG_FILE}"
