#!/bin/bash

# Make all monitoring scripts executable

cd "/Users/fabio.santos/LPD Repos/dlq-monitor"

echo "🔧 Setting executable permissions..."

chmod +x start_monitor.sh
chmod +x check_status.sh
chmod +x claude_status_monitor.py
chmod +x claude_live_monitor.py
chmod +x manual_investigation.py
chmod +x test_enhanced_investigation.py

echo "✅ All scripts are now executable"
echo ""
echo "📊 Available status monitoring commands:"
echo "  ./start_monitor.sh status  - Full status check"
echo "  ./start_monitor.sh live    - Live monitoring"
echo "  ./start_monitor.sh logs    - Tail logs"
echo "  ./check_status.sh          - Direct status check"
