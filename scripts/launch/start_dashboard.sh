#!/bin/bash

# BHiveQ Dashboard Launcher
# Starts only the web dashboards (NeuroCenter + Web Dashboard)

set -e

# Colors
ORANGE='\033[38;5;208m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

# Change to project root
cd "$(dirname "$0")/../.." || exit 1

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  🚀 BHiveQ Dashboard Launcher${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

# Setup environment
export AWS_PROFILE=FABIO-PROD
export AWS_REGION=sa-east-1
export PYTHONWARNINGS="ignore"
export PYTHONPATH="${PWD}/src:${PWD}"

# Activate venv
source venv/bin/activate 2>/dev/null || {
    echo -e "${RED}❌ Virtual environment not found. Please run: make dev${NC}"
    exit 1
}

# Install deps silently
pip install -q SQLAlchemy flask-sqlalchemy 2>/dev/null

# Start NeuroCenter
echo -e "${ORANGE}🧠 Starting NeuroCenter on port 5002...${NC}"
FLASK_PORT=5002 python -W ignore src/dlq_monitor/web/app.py 2>&1 | grep -v blake2 &
NEURO_PID=$!

# Start Web Dashboard
echo -e "${BLUE}📊 Starting Web Dashboard on port 5001...${NC}"
FLASK_PORT=5001 python -W ignore src/dlq_monitor/web/app.py 2>&1 | grep -v blake2 &
WEB_PID=$!

# Wait and show URLs
sleep 3
echo ""
echo -e "${GREEN}✅ Dashboards Started!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${ORANGE}  🧠 NeuroCenter:    http://localhost:5002/neurocenter${NC}"
echo -e "${BLUE}  📊 Web Dashboard:  http://localhost:5001/${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Press Ctrl+C to stop all dashboards"
echo ""

# Save PIDs
echo "$NEURO_PID" > .pids/neurocenter.pid
echo "$WEB_PID" > .pids/web_dashboard.pid

# Wait for interrupt
trap "kill $NEURO_PID $WEB_PID 2>/dev/null; echo ''; echo 'Dashboards stopped.'; exit" INT
wait