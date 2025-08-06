#!/bin/bash
# BHiveQ Observability Hub - Stop All Services

echo ""
echo "  🛑 Stopping BHiveQ Observability Hub Services"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Kill Web Dashboard
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    lsof -ti:5001 | xargs kill -9 2>/dev/null
    echo "  ✅ Web Dashboard stopped"
else
    echo "  ℹ️  Web Dashboard not running"
fi

# Kill ADK Monitor
if pgrep -f "adk_monitor.py" > /dev/null ; then
    pkill -f "adk_monitor.py"
    echo "  ✅ ADK Monitor stopped"
else
    echo "  ℹ️  ADK Monitor not running"
fi

# Kill any Flask apps
if pgrep -f "flask" > /dev/null ; then
    pkill -f "flask" 2>/dev/null || true
    echo "  ✅ Flask services stopped"
fi

# Kill any DLQ monitoring processes
if pgrep -f "dlq.*monitor" > /dev/null ; then
    pkill -f "dlq.*monitor" 2>/dev/null || true
    echo "  ✅ DLQ monitors stopped"
fi

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ All services stopped successfully"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""