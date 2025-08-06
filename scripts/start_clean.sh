#!/bin/bash
# Ultra-Clean Integrated Launcher - No warnings, just results

set -e

cd "$(dirname "$0")/.."

clear
echo ""
echo "  🎨 LPD Digital Hive - DLQ Operations Center"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📍 http://localhost:5001"
echo "  ⌨️  Ctrl+C to stop"
echo ""

# Activate venv silently
source venv/bin/activate 2>/dev/null || true

# Load environment
[ -f ".env" ] && export $(grep -v '^#' .env | xargs) 2>/dev/null

# Set environment
export AWS_PROFILE="${AWS_PROFILE:-FABIO-PROD}"
export AWS_REGION="${AWS_REGION:-sa-east-1}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || echo '')}"
export PYTHONWARNINGS="ignore"
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Cleanup function
cleanup() {
    echo ""
    echo "  👋 Shutting down..."
    pkill -P $$ 2>/dev/null || true
    exit 0
}

trap cleanup EXIT INT TERM

# Start both services with complete suppression
echo "  🚀 Starting services..."

# ADK Monitor (silent)
(
    exec 2>/dev/null
    python3 -W ignore scripts/monitoring/adk_monitor.py &
) &

# Web Dashboard (silent) 
(
    exec 2>/dev/null
    python3 -W ignore src/dlq_monitor/web/app.py &
) &

echo "  ✅ All services running!"
echo ""
echo "  📊 Dashboard: http://localhost:5001"
echo "  🤖 ADK agents monitoring in background"
echo ""

# Keep running
while true; do
    sleep 60
done