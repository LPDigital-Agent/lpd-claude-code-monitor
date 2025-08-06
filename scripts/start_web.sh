#!/bin/bash
# LPD Digital Hive - Web Dashboard Launcher

cd "$(dirname "$0")/.."

echo ""
echo "  🎨 LPD Digital Hive - DLQ Operations Center"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📍 http://localhost:5001"
echo "  ⌨️  Ctrl+C to stop"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "  🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Set environment variables
export AWS_PROFILE="${AWS_PROFILE:-FABIO-PROD}"
export AWS_REGION="${AWS_REGION:-sa-east-1}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || echo '')}"
export PYTHONWARNINGS="ignore"
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Run the Flask app directly
echo "  🚀 Starting dashboard..."
echo ""
python3 src/dlq_monitor/web/app.py 2>&1 | grep -v "Blake2" | grep -v "ValueError"