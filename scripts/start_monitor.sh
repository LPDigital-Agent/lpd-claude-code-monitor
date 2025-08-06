#!/bin/bash

# Enhanced DLQ Monitor Launcher for FABIO-PROD
# Automatically handles virtual environment activation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "🚀 Financial Move DLQ Monitor Launcher"
echo "📂 Project: $PROJECT_ROOT"
echo "🔑 Profile: FABIO-PROD"
echo "🌍 Region: sa-east-1"
echo "=================================="

# Check if virtual environment exists in project root
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install package in development mode if not already installed
if ! pip show lpd-claude-code-monitor > /dev/null 2>&1; then
    echo "📦 Installing package in development mode..."
    pip install -e . > /dev/null 2>&1
    echo "✅ Package installed"
fi

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
    echo "  🚀 ADK MULTI-AGENT SYSTEM:"
    echo "    ./start_monitor.sh adk-production          # ADK production monitoring"
    echo "    ./start_monitor.sh adk-test [cycles]       # Test ADK system"
    echo ""
    echo "  🔍 STATUS & MONITORING:"
    echo "    ./start_monitor.sh status                  # Check Claude investigation status"
    echo "    ./start_monitor.sh live                    # Live monitoring dashboard"
    echo "    ./start_monitor.sh enhanced                # 🎆 Enhanced Dashboard (original)"
    echo "    ./start_monitor.sh corrections             # 🤖 Claude Corrections Monitor"
    echo "    ./start_monitor.sh fixed                   # 🚀 Fixed Enhanced Monitor"
    echo "    ./start_monitor.sh ultimate                # 💥 ULTIMATE TOP TOP MONITOR (BEST!)"
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
        dlq-production "$@"
        ;;
    
    "discover")
        echo "🔍 Discovering DLQ queues in FABIO-PROD..."
        dlq-monitor discover --profile FABIO-PROD --region sa-east-1
        ;;
    
    "test")
        CYCLES=${1:-3}
        INTERVAL=${2:-30}
        echo "🧪 Testing DLQ Monitor ($CYCLES cycles, ${INTERVAL}s interval)..."
        dlq-limited "$CYCLES" "$INTERVAL"
        ;;
    
    "cli")
        SUB_COMMAND="$1"
        shift
        echo "📊 Running CLI: $SUB_COMMAND"
        dlq-monitor "$SUB_COMMAND" --profile FABIO-PROD --region sa-east-1 "$@"
        ;;
    
    "notification-test")
        echo "🔔 Testing Mac notifications..."
        dlq-monitor test-notification --profile FABIO-PROD --region sa-east-1
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
        dlq-live
        ;;
    
    "enhanced" | "dashboard")
        echo "🚀 Starting Enhanced DLQ Investigation Dashboard..."
        dlq-dashboard
        ;;
    
    "corrections")
        echo "🤖 Starting Claude AI Corrections Monitor..."
        echo "This shows what Claude agents are actually fixing..."
        dlq-corrections
        ;;
    
    "fixed")
        echo "🚀 Starting Fixed Enhanced Monitor..."
        echo "This properly shows all Claude agents and real DLQ data..."
        dlq-fixed
        ;;
    
    "ultimate" | "top")
        echo "🚀 Starting ULTIMATE CLAUDE AI MONITOR - TOP TOP VERSION!"
        echo "🤖 This is the most comprehensive monitor with EVERYTHING!"
        dlq-ultimate
        ;;
    
    "adk-production")
        echo "🚀 Starting ADK Multi-Agent DLQ Monitor System"
        echo "🤖 6 specialized agents powered by Google Gemini"
        echo "🔧 With AWS MCP servers for native AWS integration"
        echo "⚠️  Press Ctrl+C to stop"
        echo ""
        # Run with clean output (Blake2 warnings filtered)
        ./scripts/monitoring/run_clean.sh --mode production
        ;;
    
    "adk-test")
        CYCLES=${1:-3}
        echo "🧪 Testing ADK Monitor System ($CYCLES cycles)"
        # Run with clean output (Blake2 warnings filtered)
        ./scripts/monitoring/run_clean.sh --mode test --cycles "$CYCLES"
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
