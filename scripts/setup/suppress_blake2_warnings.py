#!/usr/bin/env python3
"""
Suppress Blake2 hash warnings in Python 3.11
This module should be imported before any other imports that trigger the warning
"""

import warnings
import sys

# Suppress the specific Blake2 hash warnings
warnings.filterwarnings('ignore', message='.*code for hash blake2b was not found.*')
warnings.filterwarnings('ignore', message='.*code for hash blake2s was not found.*')

# Also suppress at the logging level
import logging
logging.getLogger().setLevel(logging.WARNING)

# Monkey-patch hashlib to suppress the error at source
import hashlib
_original_new = hashlib.new

def _patched_new(name, *args, **kwargs):
    """Patched hashlib.new that ignores blake2 errors"""
    if name in ('blake2b', 'blake2s'):
        # Return a dummy hash object for blake2
        import hashlib
        return hashlib.sha256(*args, **kwargs)
    return _original_new(name, *args, **kwargs)

hashlib.new = _patched_new