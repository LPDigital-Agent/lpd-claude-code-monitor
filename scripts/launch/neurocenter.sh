#!/bin/bash

# BHiveQ NeuroCenter Launch Script
# Professional operational intelligence dashboard for DLQ monitoring

# Change to project root first
cd "$(dirname "$0")/../.." || exit 1

echo "═══════════════════════════════════════════════════════════════════"
echo "  🧠 BHiveQ NeuroCenter - Operational Intelligence Dashboard"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Set environment variables
export FLASK_APP=src/dlq_monitor/web/app.py
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

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -q SQLAlchemy flask-sqlalchemy alembic 2>/dev/null

# Create database directory if needed
mkdir -p src/dlq_monitor/database

# Set Python path for imports
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src:$(pwd)"

# Start the NeuroCenter
echo ""
echo "🚀 Starting NeuroCenter on http://localhost:${FLASK_PORT}/neurocenter"
echo ""
echo "Note: The original dashboard remains available at http://localhost:5001"
echo ""
echo "Features:"
echo "  • Real-time agent monitoring with performance metrics"
echo "  • Investigation timeline with GitHub Actions-style UI"
echo "  • Agent-DLQ assignment matrix for automatic routing"
echo "  • Live metrics dashboard with success rates"
echo "  • Drag-and-drop module rearrangement"
echo "  • Dark mode professional UI with orange accents"
echo ""
echo "Press Ctrl+C to stop the server"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Run the Flask app directly from project root
exec python scripts/web/run_neurocenter.py 2>&1 | grep -v "blake2" | grep -v "ERROR:root:code for hash"