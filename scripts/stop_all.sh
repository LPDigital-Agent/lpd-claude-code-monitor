#!/bin/bash
# BHiveQ Observability Hub - Enhanced Stop All Services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_DIR="/tmp/bhiveq"

echo ""
echo "  🛑 Stopping BHiveQ Observability Hub Services"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to stop process gracefully
stop_process() {
    local pid=$1
    local name=$2
    
    if kill -0 $pid 2>/dev/null; then
        # Try graceful shutdown first
        kill -TERM $pid 2>/dev/null
        sleep 1
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid 2>/dev/null
        fi
        echo "  ✅ $name stopped (PID: $pid)"
        return 0
    else
        return 1
    fi
}

# Check PID files first
if [ -d "$PID_DIR" ]; then
    if [ -f "$PID_DIR/web.pid" ]; then
        WEB_PID=$(cat "$PID_DIR/web.pid")
        stop_process $WEB_PID "Web Dashboard" && rm -f "$PID_DIR/web.pid"
    fi
    
    if [ -f "$PID_DIR/adk.pid" ]; then
        ADK_PID=$(cat "$PID_DIR/adk.pid")
        stop_process $ADK_PID "ADK Monitor" && rm -f "$PID_DIR/adk.pid"
    fi
fi

# Kill Web Dashboard by port
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    lsof -ti:5001 | xargs kill -9 2>/dev/null
    echo "  ✅ Web Dashboard stopped (port 5001)"
fi

# Kill ADK Monitor processes
if pgrep -f "adk_monitor.py" > /dev/null ; then
    pkill -TERM -f "adk_monitor.py" 2>/dev/null
    sleep 1
    pkill -9 -f "adk_monitor.py" 2>/dev/null || true
    echo "  ✅ ADK Monitor processes stopped"
fi

# Kill monitoring scripts
if pgrep -f "scripts/monitoring" > /dev/null ; then
    pkill -TERM -f "scripts/monitoring" 2>/dev/null
    sleep 1
    pkill -9 -f "scripts/monitoring" 2>/dev/null || true
    echo "  ✅ Monitoring scripts stopped"
fi

# Kill Flask/Web apps
if pgrep -f "src/dlq_monitor/web/app.py" > /dev/null ; then
    pkill -TERM -f "src/dlq_monitor/web/app.py" 2>/dev/null
    sleep 1
    pkill -9 -f "src/dlq_monitor/web/app.py" 2>/dev/null || true
    echo "  ✅ Flask services stopped"
fi

# Kill any DLQ monitoring processes
if pgrep -f "dlq.*monitor" > /dev/null ; then
    pkill -TERM -f "dlq.*monitor" 2>/dev/null
    sleep 1
    pkill -9 -f "dlq.*monitor" 2>/dev/null || true
    echo "  ✅ DLQ monitors stopped"
fi

# Kill Python processes related to the project
cd "$PROJECT_ROOT"
for pid in $(ps aux | grep python | grep -E "$PROJECT_ROOT|dlq_monitor|adk_monitor" | grep -v grep | awk '{print $2}'); do
    if [ ! -z "$pid" ]; then
        kill -9 $pid 2>/dev/null && echo "  ✅ Stopped Python process $pid"
    fi
done

# Clean up PID directory
if [ -d "$PID_DIR" ]; then
    rm -rf "$PID_DIR"
fi

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ All services stopped successfully"
echo "  💡 Quick restart: ./scripts/start_integrated.sh"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""