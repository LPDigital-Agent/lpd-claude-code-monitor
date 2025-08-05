#!/bin/bash

# Enhanced DLQ Monitor Launcher for FABIO-PROD
# Automatically handles virtual environment activation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Financial Move DLQ Monitor Launcher"
echo "📂 Project: $SCRIPT_DIR"
echo "🔑 Profile: FABIO-PROD"
echo "🌍 Region: sa-east-1"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Source GitHub credentials if available
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ GitHub credentials loaded from .env"
fi

# Try to get GitHub token from gh CLI if not set
if [ -z "$GITHUB_TOKEN" ]; then
    GITHUB_TOKEN=$(gh auth token 2>/dev/null)
    if [ ! -z "$GITHUB_TOKEN" ]; then
        export GITHUB_TOKEN
        export GITHUB_USERNAME="fabio-lpd"
        echo "✅ GitHub token retrieved from gh CLI"
    else
        echo "⚠️  GitHub token not set. PR audio notifications will be disabled."
        echo "💡 To enable PR notifications:"
        echo "   1. Run: gh auth login"
        echo "   2. Or set: export GITHUB_TOKEN='your_token'"
    fi
fi

# Check if no arguments provided
if [ $# -eq 0 ]; then
    echo ""
    echo "🎯 Available Commands:"
    echo ""
    echo "  🔥 PRODUCTION MONITORING:"
    echo "    ./start_monitor.sh production              # Start continuous monitoring"
    echo "    ./start_monitor.sh production --interval 60  # Custom interval (60s)"
    echo ""
    echo "  🧪 TESTING & DISCOVERY:"
    echo "    ./start_monitor.sh discover                # Discover all DLQ queues"
    echo "    ./start_monitor.sh test [cycles] [interval] # Test monitoring (default: 3 cycles, 30s)"
    echo ""
    echo "  📊 CLI INTERFACE:"
    echo "    ./start_monitor.sh cli discover            # Rich CLI discovery"
    echo "    ./start_monitor.sh cli monitor             # Rich CLI monitoring"
    echo ""
    echo "  🔔 NOTIFICATION TESTING:"
    echo "    ./start_monitor.sh notification-test       # Test Mac notifications"
    echo "    ./start_monitor.sh voice-test              # Test ElevenLabs voice"
    echo "    ./start_monitor.sh pr-audio-test           # Test PR audio system"
    echo ""
    echo "  🤖 CLAUDE CODE TESTING:"
    echo "    ./start_monitor.sh test-claude             # Test Claude Code setup"
    echo "    ./start_monitor.sh test-execution          # Test Claude execution"
    echo ""
    echo "  🔍 STATUS & MONITORING:"
    echo "    ./start_monitor.sh status                  # Check Claude investigation status"
    echo "    ./start_monitor.sh live                    # Live monitoring dashboard"
    echo "    ./start_monitor.sh enhanced                # 🎆 ENHANCED DASHBOARD (NEW!)"
    echo "    ./start_monitor.sh logs                    # Tail investigation logs"
    echo ""
    exit 0
fi

COMMAND="$1"
shift

case "$COMMAND" in
    "production")
        echo "🔥 Starting Production DLQ Monitor with PR Audio Notifications..."
        echo "⚠️  Press Ctrl+C to stop"
        echo ""
        python3 run_production_monitor.py "$@"
        ;;
    
    "discover")
        echo "🔍 Discovering DLQ queues in FABIO-PROD..."
        python3 cli.py discover --profile FABIO-PROD --region sa-east-1
        ;;
    
    "test")
        CYCLES=${1:-3}
        INTERVAL=${2:-30}
        echo "🧪 Testing DLQ Monitor ($CYCLES cycles, ${INTERVAL}s interval)..."
        python3 run_limited_monitor.py "$CYCLES" "$INTERVAL"
        ;;
    
    "cli")
        SUB_COMMAND="$1"
        shift
        echo "📊 Running CLI: $SUB_COMMAND"
        python3 cli.py "$SUB_COMMAND" --profile FABIO-PROD --region sa-east-1 "$@"
        ;;
    
    "notification-test")
        echo "🔔 Testing Mac notifications..."
        python3 cli.py test-notification --profile FABIO-PROD --region sa-east-1
        ;;
    
    "voice-test")
        echo "🔊 Testing ElevenLabs voice..."
        python3 test_voice.py
        ;;
    
    "pr-audio-test")
        echo "🔊 Testing PR audio notification system..."
        python3 test_pr_audio.py
        ;;
    
    "test-claude")
        echo "🤖 Testing Claude Code setup..."
        python3 test_claude_code.py
        ;;
    
    "test-execution")
        echo "🚀 Testing Claude Code execution..."
        python3 test_claude_execution.py
        ;;
    
    "status")
        echo "🔍 Checking Claude investigation status..."
        bash check_status.sh
        ;;
    
    "live")
        echo "📊 Starting live Claude monitor..."
        python3 claude_live_monitor.py
        ;;
    
    "enhanced" | "dashboard")
        echo "🚀 Starting Enhanced DLQ Investigation Dashboard..."
        python3 enhanced_live_monitor.py
        ;;
    
    "logs")
        echo "📄 Tailing investigation logs..."
        echo "Press Ctrl+C to stop"
        tail -f dlq_monitor_FABIO-PROD_sa-east-1.log | grep --line-buffered -i "investigation\\|claude" --color=always
        ;;
    
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "💡 Run without arguments to see available commands"
        exit 1
        ;;
esac
