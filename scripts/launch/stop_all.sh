#!/bin/bash

# BHiveQ Stop All Services Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Change to project root
cd "$(dirname "$0")/../.." || exit 1

echo -e "${YELLOW}🛑 Stopping all BHiveQ services...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# PID directory
PID_DIR=".pids"

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="${PID_DIR}/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "  Stopping ${service_name} (PID: ${pid})..."
            kill "$pid" 2>/dev/null || true
            rm -f "$pid_file"
        else
            echo -e "  ${service_name} not running (cleaning stale PID)"
            rm -f "$pid_file"
        fi
    else
        echo -e "  ${service_name} not running"
    fi
}

# Stop all services
stop_service "neurocenter"
stop_service "web_dashboard"
stop_service "dlq_monitor"
stop_service "adk_monitor"

# Also kill any Flask processes on our ports
echo ""
echo "Checking for processes on monitoring ports..."
for port in 5001 5002; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "  Killing process on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

# Kill any remaining Python monitoring processes
echo ""
echo "Cleaning up any remaining monitoring processes..."
pkill -f "dlq_monitor" 2>/dev/null || true
pkill -f "adk_monitor" 2>/dev/null || true
pkill -f "neurocenter" 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"