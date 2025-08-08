#!/bin/bash

# Clean Web Dashboard Launcher - No Blake2 Warnings
# Runs the Enhanced DLQ Web Dashboard with fully suppressed output

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Enhanced DLQ Web Dashboard (Clean Mode)${NC}"
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
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if Flask is installed
    if ! python3 -c "import flask" 2>/dev/null; then
        echo -e "${YELLOW}Installing web dashboard dependencies...${NC}"
        pip install -q --upgrade pip
        pip install -q Flask Flask-SocketIO Flask-CORS python-socketio eventlet 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Dependencies ready${NC}"
}

# Start the Flask server with clean output
start_server() {
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  🚀 Enhanced DLQ Web Dashboard${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}📍 Dashboard URL: ${BLUE}http://localhost:5001${NC}"
    echo ""
    echo "Features:"
    echo "  • Real-time DLQ monitoring with WebSocket"
    echo "  • GitHub PR tracking and management"
    echo "  • Claude AI investigation launcher"
    echo "  • CloudWatch log viewer"
    echo "  • Interactive charts and visualizations"
    echo ""
    echo "Keyboard Shortcuts:"
    echo "  • Ctrl+R: Refresh all data"
    echo "  • Ctrl+T: Toggle dark/light theme"
    echo "  • Ctrl+C: Stop the server"
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Starting server...${NC}"
    
    # Set Flask environment variables
    export FLASK_APP="src.dlq_monitor.web.app"
    export FLASK_ENV="production"  # Use production to reduce debug output
    export FLASK_PORT="5001"
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    export PYTHONWARNINGS="ignore"
    export WERKZEUG_RUN_MAIN="true"  # Suppress werkzeug restart message
    
    # Open browser after a delay
    (sleep 3 && open_browser) &
    
    # Run the Flask app using the silent runner
    cd "$(dirname "$0")"
    exec ./venv/bin/python3 src/dlq_monitor/web/run_silent.py
}

# Open browser
open_browser() {
    URL="http://localhost:5001"
    
    # Check if running on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$URL"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open "$URL"
        fi
    fi
}

# Cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down web dashboard...${NC}"
    jobs -p | xargs -r kill 2>/dev/null || true
    echo -e "${GREEN}✅ Dashboard stopped${NC}"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Main execution
main() {
    check_environment
    install_dependencies
    start_server
}

# Run main function
main "$@"