#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
ORANGE='\033[38;5;208m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOGS_DIR="$PROJECT_ROOT/logs"
PIDS_DIR="$PROJECT_ROOT/.pids"

# Ensure directories exist
mkdir -p "$LOGS_DIR" "$PIDS_DIR"

echo -e "${CYAN}🚀 Starting Flask Backend in Production Mode...${NC}"

# Stop any existing Flask processes
pkill -f "gunicorn.*app:app" 2>/dev/null
pkill -f "python.*app.py" 2>/dev/null
sleep 1

# Set environment variables
export FLASK_PORT=5002
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
export PYTHONWARNINGS="ignore"

# Change to project root
cd "$PROJECT_ROOT"

# Start with Gunicorn
echo -e "${CYAN}  Starting Gunicorn on port 5002...${NC}"

# Use fewer workers for better resource management
gunicorn \
    --bind 0.0.0.0:5002 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile "$LOGS_DIR/gunicorn_access.log" \
    --error-logfile "$LOGS_DIR/gunicorn_error.log" \
    --log-level info \
    --daemon \
    --pid "$PIDS_DIR/neurocenter_backend_gunicorn.pid" \
    "dlq_monitor.web.app:app"

# Wait for startup
sleep 2

# Check if Gunicorn started successfully
if pgrep -f "gunicorn.*app:app" > /dev/null; then
    PID=$(cat "$PIDS_DIR/neurocenter_backend_gunicorn.pid" 2>/dev/null || pgrep -f "gunicorn.*app:app" | head -1)
    echo -e "${GREEN}  ✓ Flask backend started in production mode (PID: $PID)${NC}"
    echo -e "${GREEN}  ✓ Access at: http://localhost:5002${NC}"
    
    # Test the API
    sleep 1
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/api/dlqs | grep -q "200"; then
        echo -e "${GREEN}  ✓ API responding correctly${NC}"
    else
        echo -e "${YELLOW}  ⚠ API may still be starting up${NC}"
    fi
else
    echo -e "${RED}  ✗ Failed to start Flask backend${NC}"
    echo -e "${YELLOW}  Check logs at: $LOGS_DIR/gunicorn_error.log${NC}"
    exit 1
fi

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Flask backend is running in production mode!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"