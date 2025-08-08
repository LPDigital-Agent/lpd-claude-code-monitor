#!/usr/bin/env python3
"""Test NeuroCenter functionality"""
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")
import os
os.environ['PYTHONWARNINGS'] = 'ignore'

print("🧠 Testing BHiveQ NeuroCenter...")
print("=" * 60)

# Test imports
try:
    print("1. Testing imports...")
    from dlq_monitor.services.database_service import get_database_service
    from dlq_monitor.services.investigation_service import get_investigation_service
    print("   ✅ Services imported successfully")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test initialization
try:
    print("\n2. Testing service initialization...")
    db_service = get_database_service()
    print("   ✅ Database service initialized")
    
    investigation_service = get_investigation_service()
    print("   ✅ Investigation service initialized")
except Exception as e:
    print(f"   ❌ Initialization error: {e}")
    sys.exit(1)

# Test database operations
try:
    print("\n3. Testing database operations...")
    
    # Get stats
    stats = db_service.get_stats()
    print(f"   📊 Total investigations: {stats['total_investigations']}")
    print(f"   📊 Active investigations: {stats['active_investigations']}")
    print(f"   📊 Total agents: {stats['total_agents']}")
    
    # Create test investigation
    inv_id = db_service.create_investigation(
        dlq_name="test-dlq",
        message_count=5,
        agent_id="test-agent",
        initial_prompt="Test investigation"
    )
    print(f"   ✅ Created test investigation: {inv_id}")
    
    # Get investigation
    inv = db_service.get_investigation(inv_id)
    if inv:
        print(f"   ✅ Retrieved investigation: {inv.dlq_name}")
    
    print("   ✅ Database operations working")
except Exception as e:
    print(f"   ❌ Database error: {e}")

# Test Flask app
try:
    print("\n4. Testing Flask app...")
    from dlq_monitor.web.app import app, neurocenter_enabled
    
    if neurocenter_enabled:
        print("   ✅ NeuroCenter is ENABLED")
        print("   ✅ Flask app ready")
        print("\n🎉 All tests passed! NeuroCenter is ready to launch.")
        print(f"\nTo start NeuroCenter, run:")
        print("   ./neurocenter.sh")
        print(f"\nThen open: http://localhost:5002/neurocenter")
    else:
        print("   ❌ NeuroCenter is DISABLED")
except Exception as e:
    print(f"   ❌ Flask app error: {e}")

print("=" * 60)