#!/bin/bash

# LPD NeuroCenter Services Launcher
# This script starts both the Flask backend and Next.js frontend

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}        LPD NeuroCenter Services Launcher               ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

# Set SSL environment variables to fix AWS SDK SSL issues
export AWS_CA_BUNDLE='/Users/fabio.santos/.pyenv/versions/3.11.10/lib/python3.11/site-packages/certifi/cacert.pem'
export REQUESTS_CA_BUNDLE='/Users/fabio.santos/.pyenv/versions/3.11.10/lib/python3.11/site-packages/certifi/cacert.pem'
export PYTHONWARNINGS="ignore"

# Set AWS environment
export AWS_PROFILE=FABIO-PROD
export AWS_REGION=sa-east-1

echo -e "\n${YELLOW}📋 Environment Configuration:${NC}"
echo "   AWS Profile: $AWS_PROFILE"
echo "   AWS Region: $AWS_REGION"
echo "   SSL Bundle: Set ✓"

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Start Flask backend
echo -e "\n${YELLOW}🚀 Starting Flask Backend (Port 5002)...${NC}"
if check_port 5002; then
    echo -e "${RED}   Port 5002 is already in use. Skipping Flask startup.${NC}"
else
    # You'll need to restore the Flask app.py file for this to work
    # For now, this is a placeholder
    echo -e "${YELLOW}   Note: Flask backend source files were removed.${NC}"
    echo -e "${YELLOW}   Please restore src/dlq_monitor/web/app.py to enable backend.${NC}"
fi

# Start Next.js frontend
echo -e "\n${YELLOW}🚀 Starting Next.js Frontend (Port 3001)...${NC}"
cd lpd-neurocenter-next

if check_port 3001; then
    echo -e "${RED}   Port 3001 is already in use. Skipping Next.js startup.${NC}"
else
    npm run dev &
    NEXT_PID=$!
    echo -e "${GREEN}   Next.js started with PID: $NEXT_PID${NC}"
fi

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Services Starting:${NC}"
echo -e "${GREEN}   Frontend: http://localhost:3001${NC}"
echo -e "${GREEN}   Backend:  http://localhost:5002${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for interrupt
trap 'echo -e "\n${RED}Stopping services...${NC}"; kill $NEXT_PID 2>/dev/null; exit' INT

# Keep script running
while true; do
    sleep 1
done