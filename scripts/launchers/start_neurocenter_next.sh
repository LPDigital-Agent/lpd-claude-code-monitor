#!/bin/bash

# Start script for Next.js NeuroCenter

echo "═══════════════════════════════════════════════════════════════════"
echo "  🧠 LPD NeuroCenter Next.js - http://localhost:3001"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "  ✅ Modern Next.js 14 with App Router"
echo "  ✅ Tailwind CSS with LP Digital Hive design tokens"
echo "  ✅ Real-time WebSocket integration"
echo "  ✅ Connected to Flask backend on port 5002"
echo ""
echo "  Starting services..."
echo ""

# Kill any existing Next.js processes
pkill -f "next dev" 2>/dev/null

# Start Flask backend if not running
if ! lsof -i:5002 > /dev/null 2>&1; then
    echo "  Starting Flask backend..."
    cd /Users/fabio.santos/LPD\ Repos/lpd-claude-code-monitor
    ./start_neurocenter_clean.sh &
    sleep 3
fi

# Start Next.js frontend
cd /Users/fabio.santos/LPD\ Repos/lpd-claude-code-monitor/lpd-neurocenter-next
echo "  Starting Next.js frontend..."
npm run dev