#!/bin/bash

# Quick setup script for lpd-claude-code-monitor
echo "🔧 Setting up lpd-claude-code-monitor..."

cd ~/LPD\ Repos/lpd-claude-code-monitor

# Ensure venv exists and is activated
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "✅ Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing requirements..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo "🔧 Installing package in development mode..."
pip install -e .

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 You can now run:"
echo "   ./scripts/start_monitor.sh production"
echo ""
echo "Or use any of these commands directly:"
echo "   dlq-production     # Start production monitoring"
echo "   dlq-status        # Check status"
echo "   dlq-live          # Live monitoring"
echo "   dlq-ultimate      # Ultimate dashboard"
