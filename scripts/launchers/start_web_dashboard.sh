#!/bin/bash

# Enhanced DLQ Web Dashboard Launcher
# Real-time monitoring dashboard with MCP integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Enhanced DLQ Web Dashboard Launcher${NC}"
echo "================================================"

# Check environment
check_environment() {
    echo -e "${YELLOW}Checking environment...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        exit 1
    fi
    
    # Check AWS credentials
    if [ -z "$AWS_PROFILE" ]; then
        export AWS_PROFILE="FABIO-PROD"
        echo -e "${YELLOW}ℹ️  AWS_PROFILE not set, using default: FABIO-PROD${NC}"
    fi
    
    if [ -z "$AWS_REGION" ]; then
        export AWS_REGION="sa-east-1"
        echo -e "${YELLOW}ℹ️  AWS_REGION not set, using default: sa-east-1${NC}"
    fi
    
    # Check GitHub token
    if [ -z "$GITHUB_TOKEN" ]; then
        # Try to get from gh CLI
        if command -v gh &> /dev/null; then
            export GITHUB_TOKEN=$(gh auth token 2>/dev/null || echo "")
            if [ -n "$GITHUB_TOKEN" ]; then
                echo -e "${GREEN}✅ GitHub token loaded from gh CLI${NC}"
            fi
        fi
        
        # Check .env file
        if [ -z "$GITHUB_TOKEN" ] && [ -f .env ]; then
            source .env
        fi
        
        if [ -z "$GITHUB_TOKEN" ]; then
            echo -e "${YELLOW}⚠️  GitHub token not found - PR tracking will be limited${NC}"
        fi
    fi
    
    echo -e "${GREEN}✅ Environment check complete${NC}"
}

# Install dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing web dashboard dependencies...${NC}"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install main requirements
    pip install -q --upgrade pip
    pip install -q -r requirements.txt 2>/dev/null || true
    
    # Install web-specific requirements
    if [ -f "src/dlq_monitor/web/requirements.txt" ]; then
        pip install -q -r src/dlq_monitor/web/requirements.txt 2>/dev/null || {
            echo -e "${YELLOW}Installing Flask and dependencies...${NC}"
            pip install Flask Flask-SocketIO Flask-CORS python-socketio eventlet
        }
    fi
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Start the Flask server
start_server() {
    echo -e "${BLUE}🌐 Starting Web Dashboard Server...${NC}"
    echo "================================================"
    
    # Set Flask environment variables
    export FLASK_APP="src.dlq_monitor.web.app"
    export FLASK_ENV="development"
    export FLASK_PORT="5001"  # Use port 5001 to avoid macOS AirPlay conflict
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # Suppress Blake2 warnings
    export PYTHONWARNINGS="ignore::UserWarning"
    
    # Open browser after a delay
    (sleep 3 && open_browser) &
    
    # Start Flask server
    echo -e "${GREEN}Dashboard running at: ${BLUE}http://localhost:5001${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    # Run the Flask app with clean startup script
    cd "$(dirname "$0")"
    ./venv/bin/python3 src/dlq_monitor/web/start_web.py
}

# Open browser
open_browser() {
    URL="http://localhost:5001"
    
    # Check if running on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$URL"
    # Check if running on Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open "$URL"
        elif command -v gnome-open &> /dev/null; then
            gnome-open "$URL"
        fi
    # Check if running on Windows (Git Bash/WSL)
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        start "$URL"
    fi
}

# Cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down web dashboard...${NC}"
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    echo -e "${GREEN}✅ Dashboard stopped${NC}"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Main execution
main() {
    check_environment
    install_dependencies
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  🚀 Enhanced DLQ Web Dashboard${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Features:"
    echo "  • Real-time DLQ monitoring with WebSocket updates"
    echo "  • GitHub PR tracking and management"
    echo "  • Claude AI investigation launcher"
    echo "  • CloudWatch log viewer"
    echo "  • Interactive charts and visualizations"
    echo ""
    echo "Keyboard Shortcuts:"
    echo "  • Ctrl+R: Refresh all data"
    echo "  • Ctrl+T: Toggle dark/light theme"
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    start_server
}

# Run main function
main "$@"