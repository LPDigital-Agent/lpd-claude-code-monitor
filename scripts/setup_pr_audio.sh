#!/bin/bash
# Setup script for PR Audio Notifications in DLQ Monitor

echo "🚀 Setting up PR Audio Notifications for DLQ Monitor"
echo "===================================================="

# Navigate to project directory
cd "/Users/fabio.santos/LPD Repos/lpd-claude-code-monitor"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "===================================================="
echo "📋 CONFIGURATION REQUIRED:"
echo "===================================================="
echo ""
echo "1. Set your GitHub Personal Access Token:"
echo "   export GITHUB_TOKEN='your_github_personal_access_token'"
echo ""
echo "2. Set your GitHub username (optional, defaults to 'fabio.santos'):"
echo "   export GITHUB_USERNAME='your_github_username'"
echo ""
echo "3. Add these to your ~/.zshrc or ~/.bashrc for permanent setup:"
echo "   echo 'export GITHUB_TOKEN=\"your_token\"' >> ~/.zshrc"
echo "   echo 'export GITHUB_USERNAME=\"fabio.santos\"' >> ~/.zshrc"
echo ""
echo "===================================================="
echo "🚀 TO START MONITORING:"
echo "===================================================="
echo ""
echo "With PR audio notifications (default):"
echo "   ./start_monitor.sh production"
echo ""
echo "Without PR notifications:"
echo "   ./start_monitor.sh production --no-pr-monitoring"
echo ""
echo "Custom interval:"
echo "   ./start_monitor.sh production --interval 60"
echo ""
echo "===================================================="
echo "🔊 FEATURES:"
echo "===================================================="
echo "✅ DLQ monitoring with auto-investigation"
echo "✅ Audio notifications for PR reviews (every 10 minutes)"
echo "✅ Female voice using ElevenLabs API"
echo "✅ Mac notifications for both DLQs and PRs"
echo "✅ Automatic detection of auto-investigation PRs"
echo ""
echo "🎯 The system will notify you with audio when:"
echo "   • A new PR needs your review"
echo "   • An auto-investigation PR is created"
echo "   • Every 10 minutes while PRs remain open"
echo "   • When PRs are closed or merged"
echo ""
