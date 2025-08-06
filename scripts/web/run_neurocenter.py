#!/usr/bin/env python3
"""
BHiveQ NeuroCenter Runner
Suppresses Blake2 warnings and starts the Flask app
"""
import warnings
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root))

# Suppress all warnings including Blake2
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

# Suppress Blake2 error messages
import logging
logging.getLogger().setLevel(logging.WARNING)

# Now import and run the app
if __name__ == '__main__':
    # Import app after suppressing warnings
    from dlq_monitor.web.app import app, socketio, neurocenter_enabled, logger, Thread, background_monitor
    
    # Start background monitor
    thread = Thread(target=background_monitor)
    thread.daemon = True
    thread.start()
    
    # Get port from environment
    port = int(os.environ.get('FLASK_PORT', 5002))
    
    # Announce startup
    dashboard_type = "NeuroCenter" if neurocenter_enabled else "Enhanced DLQ Web Dashboard"
    print(f"\n🚀 Starting {dashboard_type} on http://localhost:{port}")
    if neurocenter_enabled:
        print(f"   ✅ NeuroCenter: http://localhost:{port}/neurocenter")
    else:
        print(f"   ⚠️  Running in legacy mode (database services not available)")
    print(f"   📊 Dashboard: http://localhost:{port}/")
    print("\nPress CTRL+C to quit\n")
    
    # Run the app
    socketio.run(app, debug=False, host='0.0.0.0', port=port, 
                 allow_unsafe_werkzeug=True, log_output=False)