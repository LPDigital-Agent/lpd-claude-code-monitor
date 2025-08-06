#!/bin/bash
# LPD Digital Hive - Integrated DLQ Operations Center
# Starts both ADK monitoring backend and web dashboard

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo ""
echo "  🐝 BHiveQ Observability Hub - LPD Digital Hive"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🤖 ADK Multi-Agent System + Real-time Dashboard"
echo "  📍 http://localhost:5001"
echo "  ⌨️  Ctrl+C to stop all services"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "  🔧 Activating virtual environment..."
source venv/bin/activate

# Install package if needed
if ! pip show lpd-claude-code-monitor > /dev/null 2>&1; then
    echo "  📦 Installing package..."
    pip install -e . > /dev/null 2>&1
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "  ✅ Environment variables loaded"
fi

# Set environment
export AWS_PROFILE="${AWS_PROFILE:-FABIO-PROD}"
export AWS_REGION="${AWS_REGION:-sa-east-1}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || echo '')}"
export PYTHONWARNINGS="ignore"
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "  🛑 Shutting down services..."
    
    # Kill ADK monitor if running
    if [ ! -z "$ADK_PID" ]; then
        kill $ADK_PID 2>/dev/null || true
        echo "  ✅ ADK monitor stopped"
    fi
    
    # Kill web dashboard if running
    if [ ! -z "$WEB_PID" ]; then
        kill $WEB_PID 2>/dev/null || true
        echo "  ✅ Web dashboard stopped"
    fi
    
    # Kill any remaining Python processes from this script
    pkill -P $$ 2>/dev/null || true
    
    echo "  👋 Goodbye!"
    exit 0
}

# Create PID directory
PID_DIR="/tmp/bhiveq"
mkdir -p "$PID_DIR"

# Setup trap for cleanup
trap cleanup EXIT INT TERM

# Start ADK monitoring in background
echo "  🤖 Starting ADK Multi-Agent Monitor..."
(
    export PYTHONUNBUFFERED=1
    python3 -W ignore::UserWarning scripts/monitoring/adk_monitor.py 2>&1 | \
        grep -v "blake2" | \
        grep -v "ValueError" | \
        grep -v "ERROR:root" | \
        grep -v "Traceback" | \
        grep -v "hashlib" | \
        sed 's/^/    [ADK] /' &
) &
ADK_PID=$!
echo $ADK_PID > "$PID_DIR/adk.pid"
echo "  ✅ ADK monitor running (PID: $ADK_PID)"

# Give ADK monitor time to initialize
sleep 2

# Start web dashboard in background
echo "  🌐 Starting Web Dashboard..."
(
    python3 -W ignore::UserWarning src/dlq_monitor/web/app.py 2>&1 | \
        grep -v "blake2" | \
        grep -v "ValueError" | \
        grep -v "WARNING" | \
        grep -v "ERROR:root" | \
        grep -v "Traceback" | \
        grep -v "hashlib" | \
        grep -v "RuntimeError" | \
        sed 's/^/    [WEB] /' &
) &
WEB_PID=$!
echo $WEB_PID > "$PID_DIR/web.pid"
echo "  ✅ Web dashboard running (PID: $WEB_PID)"

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ All services started successfully!"
echo "  📍 Open http://localhost:5001 in your browser"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Monitoring output:"
echo ""

# Wait for processes
wait $ADK_PID $WEB_PID