#!/bin/bash

# BHiveQ Master Launcher
# Interactive menu for all monitoring and dashboard services

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
ORANGE='\033[38;5;208m'
BOLD='\033[1m'
NC='\033[0m'

# Change to script directory
cd "$(dirname "$0")" || exit 1

# Clear screen and show header
show_header() {
    clear
    echo -e "${ORANGE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${ORANGE}     🧠 BHiveQ Monitoring System - Master Launcher${NC}"
    echo -e "${ORANGE}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Show menu
show_menu() {
    echo -e "${CYAN}${BOLD}Quick Launch:${NC}"
    echo -e "  ${GREEN}1)${NC} 🚀 Start Everything (NeuroCenter + Dashboards + Monitoring)"
    echo -e "  ${GREEN}2)${NC} 🧠 Start NeuroCenter Only (port 5002)"
    echo -e "  ${GREEN}3)${NC} 📊 Start Web Dashboards (NeuroCenter + Web Dashboard)"
    echo -e "  ${GREEN}4)${NC} 🤖 Start with ADK Multi-Agent System"
    echo ""
    echo -e "${CYAN}${BOLD}Individual Services:${NC}"
    echo -e "  ${GREEN}5)${NC} 🌐 Web Dashboard Only (port 5001)"
    echo -e "  ${GREEN}6)${NC} 🔍 DLQ Monitor (Terminal)"
    echo -e "  ${GREEN}7)${NC} 📟 Enhanced Terminal Dashboard"
    echo ""
    echo -e "${CYAN}${BOLD}Management:${NC}"
    echo -e "  ${GREEN}8)${NC} 📊 Show Service Status"
    echo -e "  ${GREEN}9)${NC} 🛑 Stop All Services"
    echo -e "  ${GREEN}10)${NC} 🔄 Restart All Services"
    echo -e "  ${GREEN}11)${NC} 📜 View Logs"
    echo ""
    echo -e "${CYAN}${BOLD}Testing:${NC}"
    echo -e "  ${GREEN}12)${NC} 🧪 Test NeuroCenter Components"
    echo -e "  ${GREEN}13)${NC} 🔊 Test Notifications"
    echo ""
    echo -e "${RED}${BOLD}q)${NC} Quit"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Make scripts executable
make_executable() {
    chmod +x scripts/launch/*.sh 2>/dev/null
    chmod +x scripts/monitoring/*.sh 2>/dev/null
    chmod +x scripts/web/*.py 2>/dev/null
    chmod +x neurocenter.sh 2>/dev/null
    chmod +x start_monitor.sh 2>/dev/null
}

# Main loop
while true; do
    show_header
    show_menu
    
    read -p "$(echo -e ${CYAN}Select option: ${NC})" choice
    
    case $choice in
        1)
            echo -e "\n${GREEN}Starting all services...${NC}"
            scripts/launch/start_integrated.sh start
            read -p "Press Enter to continue..."
            ;;
        2)
            echo -e "\n${ORANGE}Starting NeuroCenter...${NC}"
            ./neurocenter.sh
            ;;
        3)
            echo -e "\n${BLUE}Starting Web Dashboards...${NC}"
            scripts/launch/start_dashboard.sh
            ;;
        4)
            echo -e "\n${MAGENTA}Starting with ADK Multi-Agent System...${NC}"
            scripts/launch/start_integrated.sh start --with-adk
            read -p "Press Enter to continue..."
            ;;
        5)
            echo -e "\n${BLUE}Starting Web Dashboard...${NC}"
            ./start_monitor.sh web
            ;;
        6)
            echo -e "\n${GREEN}Starting DLQ Monitor...${NC}"
            ./start_monitor.sh production
            ;;
        7)
            echo -e "\n${CYAN}Starting Enhanced Terminal Dashboard...${NC}"
            ./start_monitor.sh enhanced
            ;;
        8)
            echo -e "\n${CYAN}Service Status:${NC}"
            scripts/launch/start_integrated.sh status
            read -p "Press Enter to continue..."
            ;;
        9)
            echo -e "\n${RED}Stopping all services...${NC}"
            scripts/launch/stop_all.sh
            read -p "Press Enter to continue..."
            ;;
        10)
            echo -e "\n${YELLOW}Restarting all services...${NC}"
            scripts/launch/start_integrated.sh restart
            read -p "Press Enter to continue..."
            ;;
        11)
            echo -e "\n${CYAN}Viewing logs (Ctrl+C to stop)...${NC}"
            scripts/launch/start_integrated.sh logs
            ;;
        12)
            echo -e "\n${MAGENTA}Testing NeuroCenter...${NC}"
            source venv/bin/activate 2>/dev/null
            PYTHONWARNINGS=ignore python test_neurocenter.py 2>&1 | grep -v blake2
            read -p "Press Enter to continue..."
            ;;
        13)
            echo -e "\n${YELLOW}Testing Notifications...${NC}"
            ./start_monitor.sh notification-test
            read -p "Press Enter to continue..."
            ;;
        q|Q)
            echo -e "\n${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Invalid option. Please try again.${NC}"
            sleep 1
            ;;
    esac
done