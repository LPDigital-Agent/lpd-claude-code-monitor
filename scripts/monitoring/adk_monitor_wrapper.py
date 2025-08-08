#!/usr/bin/env python3
"""
Wrapper script to run ADK monitor with Blake2 warnings suppressed
"""

import sys
import os

# Suppress Blake2 warnings before any imports
import warnings
warnings.filterwarnings('ignore')

# Redirect stderr to suppress error messages
import io
import contextlib

# Capture and filter stderr
class FilteredStderr:
    def __init__(self):
        self.terminal = sys.stderr
        self.suppress_patterns = ['blake2', 'hashlib', 'ValueError: unsupported hash type']
    
    def write(self, message):
        # Only write if message doesn't contain suppressed patterns
        if not any(pattern in str(message) for pattern in self.suppress_patterns):
            self.terminal.write(message)
    
    def flush(self):
        self.terminal.flush()

# Replace stderr with filtered version
sys.stderr = FilteredStderr()

# Now import and run the actual monitor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import with suppressed warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from scripts.monitoring.adk_monitor import ADKMonitor, main

if __name__ == "__main__":
    main()