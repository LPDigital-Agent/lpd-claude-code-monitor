#!/bin/bash

# LPD Claude Code Monitor - Master Launcher
# Use this script to launch different components of the system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display menu
show_menu() {
    clear
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  LPD Claude Code Monitor - Launch Menu${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  1) 🧠 BHiveQ NeuroCenter (Professional Dashboard)"
    echo "  2) 📊 Original Web Dashboard"
    echo "  3) 🤖 ADK Monitor (Multi-Agent System)"
    echo "  4) 🔍 Terminal Monitor (Enhanced)"
    echo "  5) 🛠️  Development Setup"
    echo "  6) 🧪 Run Tests"
    echo "  7) 🛑 Stop All Services"
    echo "  0) Exit"
    echo ""
    echo -e "${YELLOW}Select an option:${NC} "
}

# Main loop
while true; do
    show_menu
    read -p "> " choice
    
    case $choice in
        1)
            echo -e "${GREEN}Launching BHiveQ NeuroCenter...${NC}"
            ./scripts/launch/neurocenter_clean.sh
            ;;
        2)
            echo -e "${GREEN}Launching Original Web Dashboard...${NC}"
            ./scripts/launchers/start_web_dashboard.sh
            ;;
        3)
            echo -e "${GREEN}Launching ADK Monitor...${NC}"
            ./scripts/monitoring/run_adk_monitor.sh
            ;;
        4)
            echo -e "${GREEN}Launching Terminal Monitor...${NC}"
            ./scripts/start_monitor.sh enhanced
            ;;
        5)
            echo -e "${GREEN}Running Development Setup...${NC}"
            make dev
            ;;
        6)
            echo -e "${GREEN}Running Tests...${NC}"
            make test
            ;;
        7)
            echo -e "${RED}Stopping All Services...${NC}"
            ./scripts/stop_all.sh
            ;;
        0)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            sleep 2
            ;;
    esac
done