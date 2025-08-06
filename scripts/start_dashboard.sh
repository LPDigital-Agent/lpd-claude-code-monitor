#!/bin/bash
# LPD Digital Hive - DLQ Operations Center Dashboard Launcher
# Clean launcher script without Blake2 warnings

cd "$(dirname "$0")/.."

echo ""
echo "  🚀 LPD Digital Hive - DLQ Operations Center"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📍 http://localhost:5001"
echo "  ⌨️  Ctrl+C to stop"
echo ""

# Use the dashboard.sh launcher from scripts/launchers
./scripts/launchers/dashboard.sh