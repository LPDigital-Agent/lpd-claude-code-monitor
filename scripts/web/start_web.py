#!/usr/bin/env python3
"""
Web Dashboard Launcher with Blake2 Warning Suppression
Clean startup for the Enhanced DLQ Web Dashboard
"""
import warnings
import sys
import os

# Suppress Blake2 hash warnings
warnings.filterwarnings("ignore", message="code for hash blake2")
warnings.filterwarnings("ignore", category=UserWarning)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import and run the Flask app
from src.dlq_monitor.web.app import socketio, app, Thread, background_monitor, logger

if __name__ == '__main__':
    # Start background monitor thread
    thread = Thread(target=background_monitor)
    thread.daemon = True
    thread.start()
    
    # Use port 5001 to avoid conflict with macOS AirPlay Receiver
    port = int(os.environ.get('FLASK_PORT', 5001))
    
    print("🚀 Enhanced DLQ Web Dashboard")
    print("=" * 50)
    print(f"📍 Dashboard URL: http://localhost:{port}")
    print("🔑 Keyboard Shortcuts:")
    print("   • Ctrl+R: Refresh all data")
    print("   • Ctrl+T: Toggle dark/light theme")
    print("   • Ctrl+C: Stop the server")
    print("=" * 50)
    
    logger.info(f"Starting dashboard on port {port}")
    
    # Run the Flask app
    socketio.run(app, debug=True, host='0.0.0.0', port=port)