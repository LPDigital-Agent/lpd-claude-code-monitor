#!/usr/bin/env python3
"""Test NeuroCenter services"""
import warnings
warnings.filterwarnings('ignore')

import sys
import os
sys.path.insert(0, 'src')
os.environ['PYTHONWARNINGS'] = 'ignore'

try:
    print("Testing NeuroCenter services...")
    from dlq_monitor.services.database_service import get_database_service
    from dlq_monitor.services.investigation_service import get_investigation_service
    
    db = get_database_service()
    inv = get_investigation_service()
    
    print("✅ NeuroCenter services loaded successfully!")
    print("✅ Database initialized at:", db.db_path)
    print("✅ Ready to launch NeuroCenter!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure all dependencies are installed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()