#!/bin/bash

# Enhanced Claude Investigation Status Check
# Shows detailed status of all Claude sessions and their activities

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           🤖 CLAUDE INVESTIGATION STATUS MONITOR 🤖                ║"
echo "╠════════════════════════════════════════════════════════════════════╣"
echo "║  Checking all Claude sessions and investigation activities...      ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install psutil if not present (for process monitoring)
pip list | grep psutil > /dev/null 2>&1 || pip install psutil -q

echo -e "${CYAN}🔍 Running comprehensive status check...${NC}"
echo ""

# Run the enhanced status monitor
python claude_status_monitor.py

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Quick process check with ps
echo -e "${YELLOW}📊 QUICK PROCESS CHECK (via ps command):${NC}"
echo "────────────────────────────────────────────────────────────────────"

CLAUDE_PROCS=$(ps aux | grep -i claude | grep -v grep | wc -l)
if [ $CLAUDE_PROCS -gt 0 ]; then
    echo -e "${GREEN}✅ Found $CLAUDE_PROCS Claude process(es):${NC}"
    ps aux | grep -i claude | grep -v grep | while read line; do
        PID=$(echo $line | awk '{print $2}')
        CPU=$(echo $line | awk '{print $3}')
        MEM=$(echo $line | awk '{print $4}')
        TIME=$(echo $line | awk '{print $10}')
        echo -e "  ${CYAN}PID:${NC} $PID | ${CYAN}CPU:${NC} $CPU% | ${CYAN}MEM:${NC} $MEM% | ${CYAN}TIME:${NC} $TIME"
    done
else
    echo -e "${YELLOW}No Claude processes currently running${NC}"
fi

echo ""
echo "────────────────────────────────────────────────────────────────────"
echo ""

# Check last 10 investigation log entries
echo -e "${PURPLE}📜 LAST 10 INVESTIGATION LOG ENTRIES:${NC}"
echo "────────────────────────────────────────────────────────────────────"

if [ -f "dlq_monitor_FABIO-PROD_sa-east-1.log" ]; then
    grep -i "investigation\|claude" dlq_monitor_FABIO-PROD_sa-east-1.log | tail -10 | while IFS= read -r line; do
        if echo "$line" | grep -q "Starting"; then
            echo -e "${GREEN}▶ $line${NC}"
        elif echo "$line" | grep -q "completed successfully"; then
            echo -e "${GREEN}✓ $line${NC}"
        elif echo "$line" | grep -q "failed\|error"; then
            echo -e "${RED}✗ $line${NC}"
        elif echo "$line" | grep -q "timeout"; then
            echo -e "${YELLOW}⏰ $line${NC}"
        else
            echo "  $line"
        fi
    done
else
    echo -e "${RED}Log file not found${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Show current DLQ status summary
echo -e "${BLUE}📊 CURRENT DLQ SUMMARY:${NC}"
echo "────────────────────────────────────────────────────────────────────"

python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('$SCRIPT_DIR')))

try:
    from dlq_monitor import DLQMonitor, MonitorConfig
    
    config = MonitorConfig(
        aws_profile='FABIO-PROD',
        region='sa-east-1',
        auto_investigate_dlqs=[
            'fm-digitalguru-api-update-dlq-prod',
            'fm-transaction-processor-dlq-prd'
        ]
    )
    
    monitor = DLQMonitor(config)
    alerts = monitor.check_dlq_messages()
    
    total_messages = sum(alert.message_count for alert in alerts)
    
    if alerts:
        print(f'⚠️  {len(alerts)} queue(s) with messages (Total: {total_messages} messages)')
        for alert in alerts[:5]:  # Show first 5
            auto = '🤖' if alert.queue_name in config.auto_investigate_dlqs else '📋'
            print(f'  {auto} {alert.queue_name}: {alert.message_count} msgs')
    else:
        print('✅ All DLQ queues are empty')
except Exception as e:
    print(f'❌ Error checking DLQs: {e}')
" 2>/dev/null || echo -e "${RED}Could not check DLQ status${NC}"

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Show monitoring commands
echo -e "${GREEN}🔧 MONITORING COMMANDS:${NC}"
echo "────────────────────────────────────────────────────────────────────"
echo "  Watch logs:        tail -f dlq_monitor_FABIO-PROD_sa-east-1.log"
echo "  Check status:      ./check_status.sh"
echo "  Manual trigger:    python manual_investigation.py"
echo "  Test system:       python test_enhanced_investigation.py"
echo "  Start monitor:     ./start_monitor.sh production"
echo "  Kill investigation: kill -9 <PID>"
echo ""

# Check if monitor is running
MONITOR_PID=$(ps aux | grep -E "run_production_monitor|dlq_monitor" | grep -v grep | awk '{print $2}' | head -1)
if [ ! -z "$MONITOR_PID" ]; then
    echo -e "${GREEN}✅ DLQ Monitor is running (PID: $MONITOR_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  DLQ Monitor is not running${NC}"
    echo -e "   Start it with: ${CYAN}./start_monitor.sh production${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                     📊 STATUS CHECK COMPLETE 📊                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
