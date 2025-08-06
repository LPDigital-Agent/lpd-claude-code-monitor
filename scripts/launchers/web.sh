#!/bin/bash

# Ultra-simple web dashboard launcher with clean output
# Just runs the dashboard with Blake2 warnings filtered

echo "🚀 Enhanced DLQ Web Dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 URL: http://localhost:5001"
echo "   Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Set environment
export AWS_PROFILE="${AWS_PROFILE:-FABIO-PROD}"
export AWS_REGION="${AWS_REGION:-sa-east-1}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || echo '')}"
export FLASK_PORT=5001
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Activate venv and run
source venv/bin/activate 2>/dev/null || true

# Run with filtered output
python3 src/dlq_monitor/web/run_silent.py 2>&1 | \
    grep -v "ERROR:root:code for hash blake2" | \
    grep -v "ValueError: unsupported hash type" | \
    grep -v "Traceback" | \
    grep -v "File \"" | \
    grep -v "line [0-9]" | \
    grep -v "hashlib.py" | \
    grep -v "__func_name" | \
    grep -v "globals()" | \
    grep -v "KeyError:"