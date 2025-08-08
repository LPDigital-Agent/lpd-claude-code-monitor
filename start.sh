#!/bin/bash

# Main launcher script for LPD NeuroCenter
# This is a convenience wrapper for the most common operations

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}        LPD NeuroCenter - Main Launcher                 ${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"

# Set SSL environment for AWS
source scripts/setup/set_ssl_env.sh

# Default to integrated mode if no argument provided
MODE=${1:-integrated}

case $MODE in
    integrated|int)
        echo -e "${GREEN}Starting Integrated Mode (ADK + Web + Next.js)...${NC}"
        ./scripts/launch/start_integrated.sh
        ;;
    dashboard|dash)
        echo -e "${GREEN}Starting Web Dashboard only...${NC}"
        ./scripts/launch/start_dashboard.sh
        ;;
    neurocenter|nc)
        echo -e "${GREEN}Starting NeuroCenter (Next.js)...${NC}"
        ./scripts/launchers/start_neurocenter_next.sh
        ;;
    stop)
        echo -e "${YELLOW}Stopping all services...${NC}"
        ./scripts/launch/stop_all.sh
        ;;
    help|--help|-h)
        echo -e "${GREEN}Usage: ./start.sh [mode]${NC}"
        echo ""
        echo "Available modes:"
        echo "  integrated (default) - Start all services (ADK + Web Dashboard + Next.js)"
        echo "  dashboard           - Start Web Dashboard only"
        echo "  neurocenter         - Start NeuroCenter Next.js only"
        echo "  stop                - Stop all services"
        echo ""
        echo "Examples:"
        echo "  ./start.sh              # Start integrated mode"
        echo "  ./start.sh dashboard    # Start dashboard only"
        echo "  ./start.sh stop         # Stop all services"
        ;;
    *)
        echo -e "${YELLOW}Unknown mode: $MODE${NC}"
        echo "Use './start.sh help' for usage information"
        exit 1
        ;;
esac