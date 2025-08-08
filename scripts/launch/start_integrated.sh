#!/bin/bash

# BHiveQ Integrated System Launcher
# Starts all monitoring and NeuroCenter components

# Don't exit on error - handle errors gracefully
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
ORANGE='\033[38;5;208m'
NC='\033[0m' # No Color

# Change to project root
cd "$(dirname "$0")/../.." || exit 1
PROJECT_ROOT=$(pwd)

# PID file locations
PID_DIR="${PROJECT_ROOT}/.pids"
mkdir -p "$PID_DIR"

# Log directory
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"

# Function to print colored messages
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="${PID_DIR}/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            print_color "$YELLOW" "  Stopping ${service_name} (PID: ${pid})..."
            kill "$pid" 2>/dev/null || true
            rm -f "$pid_file"
            sleep 1
        else
            rm -f "$pid_file"
        fi
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local command=$2
    local port=$3
    local log_file="${LOG_DIR}/${service_name}.log"
    local pid_file="${PID_DIR}/${service_name}.pid"
    
    # Check if already running
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            print_color "$GREEN" "  ✓ ${service_name} already running (PID: ${pid})"
            return 0
        fi
    fi
    
    # Check port if specified
    if [ -n "$port" ]; then
        if check_port "$port"; then
            print_color "$RED" "  ✗ Port ${port} is already in use"
            return 1
        fi
    fi
    
    # Start the service
    print_color "$CYAN" "  Starting ${service_name}..."
    eval "$command" > "$log_file" 2>&1 &
    local pid=$!
    echo "$pid" > "$pid_file"
    
    # Wait a moment and check if it started
    sleep 2
    if kill -0 "$pid" 2>/dev/null; then
        print_color "$GREEN" "  ✓ ${service_name} started (PID: ${pid})"
        return 0
    else
        print_color "$RED" "  ✗ Failed to start ${service_name}"
        rm -f "$pid_file"
        return 1
    fi
}

# Function to show status
show_status() {
    print_color "$CYAN" "\n📊 Service Status:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local services=("neurocenter_backend" "neurocenter_next" "web_dashboard" "dlq_monitor" "adk_monitor")
    for service in "${services[@]}"; do
        local pid_file="${PID_DIR}/${service}.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                print_color "$GREEN" "  ✓ ${service}: Running (PID: ${pid})"
            else
                print_color "$RED" "  ✗ ${service}: Stopped (stale PID file)"
            fi
        else
            print_color "$YELLOW" "  - ${service}: Not running"
        fi
    done
    echo ""
}

# Function to stop all services
stop_all() {
    print_color "$YELLOW" "\n🛑 Stopping all services..."
    stop_service "adk_monitor"
    stop_service "dlq_monitor"
    stop_service "web_dashboard"
    stop_service "neurocenter_next"
    stop_service "neurocenter_backend"
    print_color "$GREEN" "✓ All services stopped\n"
}

# Function to start all services
start_all() {
    print_color "$CYAN" "\n🚀 Starting BHiveQ Integrated System..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Setup environment
    export AWS_PROFILE=FABIO-PROD
    export AWS_REGION=sa-east-1
    export PYTHONWARNINGS="ignore"
    export PYTHONPATH="${PROJECT_ROOT}/src:${PROJECT_ROOT}"
    
    # Check for Python 3.13 virtual environment first, then fallback to regular venv
    if [ -d "venv-313" ]; then
        source venv-313/bin/activate 2>/dev/null && print_color "$GREEN" "  ✓ Python 3.13 virtual environment activated"
        # Fix SSL certificates for AWS SDK - Python 3.13
        export AWS_CA_BUNDLE="${PROJECT_ROOT}/venv-313/lib/python3.13/site-packages/certifi/cacert.pem"
        export REQUESTS_CA_BUNDLE="${PROJECT_ROOT}/venv-313/lib/python3.13/site-packages/certifi/cacert.pem"
    elif [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null && print_color "$GREEN" "  ✓ Virtual environment activated"
        # Fix SSL certificates for AWS SDK - fallback
        export AWS_CA_BUNDLE='/Users/fabio.santos/.pyenv/versions/3.11.10/lib/python3.11/site-packages/certifi/cacert.pem'
        export REQUESTS_CA_BUNDLE='/Users/fabio.santos/.pyenv/versions/3.11.10/lib/python3.11/site-packages/certifi/cacert.pem'
    else
        print_color "$YELLOW" "  ⚠ Using system Python (virtual environment not found)"
        # Fix SSL certificates for AWS SDK - system Python
        export AWS_CA_BUNDLE='/Users/fabio.santos/.pyenv/versions/3.11.10/lib/python3.11/site-packages/certifi/cacert.pem'
        export REQUESTS_CA_BUNDLE='/Users/fabio.santos/.pyenv/versions/3.11.10/lib/python3.11/site-packages/certifi/cacert.pem'
    fi
    
    # Install dependencies silently
    print_color "$CYAN" "\n📦 Checking dependencies..."
    pip install -q SQLAlchemy flask-sqlalchemy google-adk google-generativeai 2>/dev/null
    
    # 1. Start NeuroCenter Backend (Port 5002)
    print_color "$ORANGE" "\n🧠 NeuroCenter Backend Service"
    start_service "neurocenter_backend" \
        "FLASK_PORT=5002 python -W ignore src/dlq_monitor/web/app.py" \
        "5002"
    
    # 2. Start NeuroCenter Next.js Frontend (Port 3001)
    print_color "$ORANGE" "\n⚛️  NeuroCenter Next.js Frontend"
    cd lpd-neurocenter-next && npm install --silent 2>/dev/null && cd ..
    start_service "neurocenter_next" \
        "cd lpd-neurocenter-next && npm run dev" \
        "3001"
    
    # 3. Start Web Dashboard (Port 5001)
    print_color "$BLUE" "\n📊 Web Dashboard Service"
    start_service "web_dashboard" \
        "FLASK_PORT=5001 python -W ignore src/dlq_monitor/web/app.py" \
        "5001"
    
    # 4. Start DLQ Monitor
    print_color "$GREEN" "\n🔍 DLQ Monitor Service"
    start_service "dlq_monitor" \
        "python -W ignore src/dlq_monitor/core/monitor.py" \
        ""
    
    # 5. Start ADK Production Monitor (always start for production)
    print_color "$MAGENTA" "\n🤖 ADK Multi-Agent Production Monitor"
    start_service "adk_monitor" \
        "python -W ignore scripts/monitoring/adk_production_monitor.py" \
        ""
    
    # Show final status
    show_status
    
    # Display access URLs
    print_color "$CYAN" "🌐 Access URLs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$ORANGE" "  ⚛️  NeuroCenter Next.js:  http://localhost:3001/"
    print_color "$ORANGE" "  🧠 NeuroCenter Flask:     http://localhost:5002/neurocenter"
    print_color "$BLUE" "  📊 Web Dashboard:         http://localhost:5001/"
    print_color "$GREEN" "  📝 Logs:                  ${LOG_DIR}/"
    echo ""
    
    # Show control commands
    print_color "$CYAN" "🎮 Control Commands:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Status:  $0 status"
    echo "  Stop:    $0 stop"
    echo "  Restart: $0 restart"
    echo "  Logs:    tail -f ${LOG_DIR}/<service>.log"
    echo ""
}

# Function to tail logs
tail_logs() {
    print_color "$CYAN" "\n📜 Tailing all service logs (Ctrl+C to stop)..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    tail -f ${LOG_DIR}/*.log 2>/dev/null
}

# Main script logic
case "${1:-start}" in
    start)
        start_all "$2"
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        start_all "$2"
        ;;
    status)
        show_status
        ;;
    logs)
        tail_logs
        ;;
    *)
        print_color "$CYAN" "BHiveQ Integrated System Launcher"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status"
        echo "  logs     - Tail all service logs"
        echo ""
        echo "Options:"
        echo "  --with-adk, -a  - Also start ADK multi-agent monitor"
        echo ""
        echo "Examples:"
        echo "  $0                    # Start all services"
        echo "  $0 start --with-adk   # Start with ADK monitor"
        echo "  $0 status             # Check service status"
        echo "  $0 stop               # Stop all services"
        ;;
esac