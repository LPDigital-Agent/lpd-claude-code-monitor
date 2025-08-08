#!/bin/bash

# Quick NeuroCenter launcher with clean output

cd "$(dirname "$0")" || exit 1

# Set environment
export FLASK_PORT=5002
export AWS_PROFILE=FABIO-PROD
export AWS_REGION=sa-east-1
export PYTHONWARNINGS="ignore::UserWarning"
export PYTHONHASHSEED=0
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src:$(pwd)"

# Suppress blake2 warnings
export PYTHONWARNINGS="ignore"

# Activate venv
source venv/bin/activate 2>/dev/null

# Install deps silently
pip install -q SQLAlchemy flask-sqlalchemy 2>/dev/null

clear

echo "═══════════════════════════════════════════════════════════════════"
echo "  🧠 BHiveQ NeuroCenter - http://localhost:5002/neurocenter"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "  ✅ Manual investigation mode ENABLED"
echo "  ✅ Database cleaned on startup"
echo ""

# Use system Python instead of pyenv Python to avoid blake2 issues
exec /usr/bin/python3 -W ignore src/dlq_monitor/web/app.py 2>&1 | grep -v "blake2" | grep -v "ValueError.*blake2" | grep -v "ERROR:root" | grep -v "unsupported hash type"