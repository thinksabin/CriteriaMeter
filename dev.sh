#!/usr/bin/env bash
# dev.sh — stop, rebuild, and restart CriteriaMeter (backend + frontend)
# Usage: ./dev.sh [--remap]
#   --remap   re-run the mapping pipeline before starting (regenerates unified_mapping.json)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_LOG="$SCRIPT_DIR/.backend.log"
FRONTEND_LOG="$SCRIPT_DIR/.frontend.log"
# Ports default here; overridden from config.yml after the venv is ready (see Step 2)
BACKEND_PORT=8000
FRONTEND_PORT=3000
REMAP=false

# ── Parse arguments ────────────────────────────────────────────────────────────
for arg in "$@"; do
  case $arg in
    --remap) REMAP=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

# ── Helpers ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

info()    { echo -e "${GREEN}[dev]${NC} $*"; }
warning() { echo -e "${YELLOW}[dev]${NC} $*"; }
error()   { echo -e "${RED}[dev]${NC} $*" >&2; }

wait_for_port() {
  local port=$1 label=$2 attempts=0 max=30
  while ! curl -sf "http://localhost:${port}/health" >/dev/null 2>&1 && \
        ! curl -sf "http://localhost:${port}/" >/dev/null 2>&1; do
    attempts=$((attempts + 1))
    if [ $attempts -ge $max ]; then
      error "$label did not become ready on :${port} after ${max}s"
      error "Check log: $([ "$port" = "$BACKEND_PORT" ] && echo "$BACKEND_LOG" || echo "$FRONTEND_LOG")"
      exit 1
    fi
    sleep 1
  done
}

# ── Step 1: stop any running processes ────────────────────────────────────────
info "Stopping existing processes…"
pkill -f "uvicorn app.main" 2>/dev/null && info "  stopped backend" || true
pkill -f "vite"             2>/dev/null && info "  stopped frontend" || true
sleep 1   # give ports time to release

# ── Step 2: validate environment ──────────────────────────────────────────────
info "Checking environment…"

if [ ! -f "$BACKEND_DIR/.venv/bin/uvicorn" ]; then
  info "  creating Python virtual environment…"
  python3 -m venv "$BACKEND_DIR/.venv"
fi

info "  installing Python dependencies…"
"$BACKEND_DIR/.venv/bin/pip" install --quiet -r "$BACKEND_DIR/requirements.txt"

# Read ports from config.yml now that PyYAML is installed in the venv
_ports=$("$BACKEND_DIR/.venv/bin/python" - "$SCRIPT_DIR/config.yml" <<'PYEOF' 2>/dev/null
import sys, yaml
try:
    cfg = yaml.safe_load(open(sys.argv[1])) or {}
    s = cfg.get("server", {})
    print(s.get("backend_port", 8000), s.get("frontend_port", 3000))
except Exception:
    print("8000 3000")
PYEOF
)
BACKEND_PORT=$(echo "$_ports" | awk '{print $1}')
FRONTEND_PORT=$(echo "$_ports" | awk '{print $2}')
info "  config: backend_port=${BACKEND_PORT}, frontend_port=${FRONTEND_PORT}"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  info "  installing Node dependencies…"
  (cd "$FRONTEND_DIR" && npm install --silent)
fi

# ── Step 3: regenerate mapping (optional or if JSON is missing) ────────────────
MAPPING_JSON="$BACKEND_DIR/app/mapping/output/unified_mapping.json"
if [ "$REMAP" = true ] || [ ! -f "$MAPPING_JSON" ]; then
  info "Regenerating unified mapping…"
  (cd "$BACKEND_DIR" && .venv/bin/python -m app.mapping.run_mapping)
else
  info "Mapping JSON up to date — skipping (pass --remap to force)"
fi

# ── Step 4: start backend ─────────────────────────────────────────────────────
info "Starting backend on :${BACKEND_PORT}…"
(cd "$BACKEND_DIR" && \
  .venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$BACKEND_PORT" \
  > "$BACKEND_LOG" 2>&1) &
BACKEND_PID=$!

info "  waiting for backend to be ready…"
wait_for_port "$BACKEND_PORT" "backend"
info "  backend ready (pid $BACKEND_PID)"

# ── Step 5: start frontend ────────────────────────────────────────────────────
info "Starting frontend on :${FRONTEND_PORT}…"
(cd "$FRONTEND_DIR" && npm run dev > "$FRONTEND_LOG" 2>&1) &
FRONTEND_PID=$!

info "  waiting for frontend to be ready…"
wait_for_port "$FRONTEND_PORT" "frontend"
info "  frontend ready (pid $FRONTEND_PID)"

# ── Done ───────────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${GREEN}●${NC} Frontend   http://localhost:${FRONTEND_PORT}"
echo -e "  ${GREEN}●${NC} Backend    http://localhost:${BACKEND_PORT}"
echo -e "  ${GREEN}●${NC} API docs   http://localhost:${BACKEND_PORT}/docs"
echo ""
echo -e "  Logs:  $BACKEND_LOG"
echo -e "         $FRONTEND_LOG"
echo ""
echo -e "  Run ${YELLOW}./dev.sh --remap${NC} to also regenerate the mapping JSON."
echo -e "  Run ${YELLOW}pkill -f uvicorn; pkill -f vite${NC} to stop both servers."
