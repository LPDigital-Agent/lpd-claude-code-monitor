#!/usr/bin/env python3
"""
Simple Web Dashboard Runner
"""
import os
import sys

# Suppress warnings before imports
import warnings
warnings.filterwarnings("ignore")

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set port
os.environ['FLASK_PORT'] = '5001'

# Import and run
from src.dlq_monitor.web.app import socketio, app, Thread, background_monitor

if __name__ == '__main__':
    # Start background thread
    thread = Thread(target=background_monitor)
    thread.daemon = True
    thread.start()
    
    port = 5001
    print(f"\n🚀 Dashboard: http://localhost:{port}")
    print("   Press Ctrl+C to stop\n")
    
    # Run app
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)