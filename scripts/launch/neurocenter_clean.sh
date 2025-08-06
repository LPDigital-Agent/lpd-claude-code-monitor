#!/bin/bash

# BHiveQ NeuroCenter Launch Script - Clean Version
# Professional operational intelligence dashboard for DLQ monitoring

clear

echo "═══════════════════════════════════════════════════════════════════"
echo "  🧠 BHiveQ NeuroCenter - Operational Intelligence Dashboard"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Set environment variables
export FLASK_ENV=production
export FLASK_PORT=5002
export AWS_PROFILE=FABIO-PROD
export AWS_REGION=sa-east-1
export PYTHONWARNINGS="ignore"
export PYTHONHASHSEED=0

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: make dev"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies silently if needed
pip install -q SQLAlchemy flask-sqlalchemy alembic 2>/dev/null

# Create database directory if needed
mkdir -p src/dlq_monitor/database

echo "🚀 Starting NeuroCenter..."
echo ""
echo "   Access points:"
echo "   • NeuroCenter: http://localhost:${FLASK_PORT}/neurocenter"
echo "   • Dashboard:   http://localhost:${FLASK_PORT}/"
echo ""
echo "Press Ctrl+C to stop"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Set Python path for imports
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src:$(pwd)"

# Run the Flask app directly
cd src/dlq_monitor/web
exec python ../../../scripts/web/run_neurocenter.py 2>&1 | grep -v "blake2" | grep -v "ERROR:root:code for hash"