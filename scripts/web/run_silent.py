#!/usr/bin/env python3
"""
Silent Web Dashboard Runner
Completely suppresses Blake2 warnings and unnecessary output
"""
import warnings
import sys
import os
import logging

# Suppress ALL warnings before any imports
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

# Suppress logging from various libraries
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# Redirect stderr to suppress any remaining warnings
class SuppressBlake2:
    def write(self, text):
        if 'blake2' not in text.lower() and 'hash' not in text.lower():
            sys.__stderr__.write(text)
    def flush(self):
        sys.__stderr__.flush()

sys.stderr = SuppressBlake2()

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# Now import Flask app
from src.dlq_monitor.web.app import socketio, app, Thread, background_monitor

if __name__ == '__main__':
    # Start background monitor
    thread = Thread(target=background_monitor)
    thread.daemon = True
    thread.start()
    
    # Get port
    port = int(os.environ.get('FLASK_PORT', 5001))
    
    # Simple status message
    print(f"\n✅ Dashboard running at http://localhost:{port}")
    print("   Press Ctrl+C to stop\n")
    
    # Run Flask with minimal output
    try:
        socketio.run(
            app, 
            debug=False, 
            host='0.0.0.0', 
            port=port,
            log_output=False,
            allow_unsafe_werkzeug=True  # Required for socketio in non-debug mode
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")