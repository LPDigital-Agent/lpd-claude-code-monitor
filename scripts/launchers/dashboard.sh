#!/bin/bash

# Ultra-Clean Dashboard Launcher
# The simplest, cleanest way to run the web dashboard

echo ""
echo "  🚀 DLQ Web Dashboard"
echo "  ━━━━━━━━━━━━━━━━━━━━━"
echo "  📍 http://localhost:5001"
echo "  ⌨️  Ctrl+C to stop"
echo ""

# Set minimal environment
export AWS_PROFILE="${AWS_PROFILE:-FABIO-PROD}"
export AWS_REGION="${AWS_REGION:-sa-east-1}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || echo '')}"
export PYTHONWARNINGS="ignore"

# Run with all output suppressed except essentials
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null

python3 -c "
import warnings; warnings.filterwarnings('ignore')
import sys; sys.path.insert(0, '.')
from src.dlq_monitor.web.app import socketio, app, Thread, background_monitor
thread = Thread(target=background_monitor); thread.daemon = True; thread.start()
print('  ✅ Running...\n')
socketio.run(app, host='0.0.0.0', port=5001, debug=False, log_output=False, allow_unsafe_werkzeug=True)
" 2>&1 | grep -v "ERROR:root" | grep -v "ValueError" | grep -v "Traceback" | grep -v "WARNING"