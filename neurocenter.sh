#!/bin/bash

# Quick NeuroCenter launcher with clean output

cd "$(dirname "$0")" || exit 1

# Set environment
export FLASK_PORT=5002
export AWS_PROFILE=FABIO-PROD
export AWS_REGION=sa-east-1
export PYTHONWARNINGS="ignore"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src:$(pwd)"

# Activate venv
source venv/bin/activate 2>/dev/null

# Install deps silently
pip install -q SQLAlchemy flask-sqlalchemy 2>/dev/null

clear

echo "═══════════════════════════════════════════════════════════════════"
echo "  🧠 BHiveQ NeuroCenter - http://localhost:5002/neurocenter"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Run with all warnings suppressed
exec python -W ignore src/dlq_monitor/web/app.py 2>&1 | grep -v "blake2" | grep -v "ERROR:root"