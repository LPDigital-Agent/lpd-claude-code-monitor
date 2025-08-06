#!/bin/bash
# BHiveQ Observability Hub - Service Status Check

echo ""
echo "  🐝 BHiveQ Observability Hub - Service Status"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Web Dashboard
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "  ✅ Web Dashboard: Running on port 5001"
    echo "     📍 http://localhost:5001"
else
    echo "  ❌ Web Dashboard: Not running"
fi

# Check ADK Monitor
if pgrep -f "adk_monitor.py" > /dev/null ; then
    PID=$(pgrep -f "adk_monitor.py")
    echo "  ✅ ADK Monitor: Running (PID: $PID)"
else
    echo "  ❌ ADK Monitor: Not running"
fi

# Check for any DLQ monitoring processes
if pgrep -f "dlq.*monitor" > /dev/null ; then
    echo "  ✅ DLQ Monitoring: Active"
else
    echo "  ⚠️  DLQ Monitoring: No active monitors"
fi

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Quick Commands:"
echo "  • Start all:     ./scripts/start_integrated.sh"
echo "  • Dashboard only: ./scripts/start_dashboard.sh"
echo "  • Stop all:      ./scripts/stop_all.sh"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""