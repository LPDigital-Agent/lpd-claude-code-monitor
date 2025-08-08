#!/bin/bash

# Clean NeuroCenter launcher with proper dependencies

cd "$(dirname "$0")" || exit 1

# Set environment
export FLASK_PORT=5002
export AWS_PROFILE=FABIO-PROD
export AWS_REGION=sa-east-1
export PYTHONWARNINGS="ignore"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src:$(pwd)"

# Kill any existing processes
pkill -f "python.*app.py" 2>/dev/null

# Clear database
rm -f src/dlq_monitor/database/neurocenter.db

clear

echo "═══════════════════════════════════════════════════════════════════"
echo "  🧠 BHiveQ NeuroCenter - http://localhost:5002/neurocenter"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "  ✅ Manual investigation mode ENABLED"
echo "  ✅ Database cleaned on startup"
echo "  ✅ No automatic investigations"
echo ""

# Run with system Python and all warnings suppressed
exec /usr/bin/python3 -W ignore src/dlq_monitor/web/app.py 2>&1 | \
    grep -v "blake2" | \
    grep -v "ValueError" | \
    grep -v "ERROR:root" | \
    grep -v "unsupported hash type" | \
    grep -v "WARNING:werkzeug"