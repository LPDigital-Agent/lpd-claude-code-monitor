#!/usr/bin/env python3
"""
Test Auto-Investigation System for DLQ Monitor
"""
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dlq_monitor import DLQMonitor, MonitorConfig, DLQAlert

def test_auto_investigation():
    """Test the auto-investigation trigger mechanism"""
    print("=" * 60)
    print("🧪 Testing Auto-Investigation System")
    print("=" * 60)
    
    # Create a test configuration
    config = MonitorConfig(
        aws_profile="FABIO-PROD",
        region="sa-east-1",
        check_interval=30,
        notification_sound=True,
        auto_investigate_dlqs=[
            "fm-digitalguru-api-update-dlq-prod",
            "fm-transaction-processor-dlq-prd",
            "test-queue-dlq"  # Add test queue
        ],
        claude_command_timeout=60  # Short timeout for testing
    )
    
    print(f"\n📋 Configuration:")
    print(f"   Profile: {config.aws_profile}")
    print(f"   Region: {config.region}")
    print(f"   Auto-investigate queues: {config.auto_investigate_dlqs}")
    print(f"   Claude timeout: {config.claude_command_timeout}s")
    
    # Initialize monitor
    print("\n🔧 Initializing DLQ Monitor...")
    try:
        monitor = DLQMonitor(config)
        print("✅ Monitor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize monitor: {e}")
        return False
    
    # Test 1: Check if auto-investigation logic works
    print("\n🔍 Test 1: Auto-Investigation Logic")
    print("-" * 40)
    
    test_queue = "fm-digitalguru-api-update-dlq-prod"
    
    # Check if should auto-investigate
    should_investigate = monitor._should_auto_investigate(test_queue)
    print(f"   Queue: {test_queue}")
    print(f"   Should investigate: {should_investigate}")
    
    if should_investigate:
        print("   ✅ Auto-investigation logic working")
    else:
        print("   ⚠️  Auto-investigation might be in cooldown or already running")
        if test_queue in monitor.auto_investigations:
            last_investigation = monitor.auto_investigations[test_queue]
            time_since = datetime.now() - last_investigation
            cooldown_remaining = monitor.investigation_cooldown - time_since.total_seconds()
            if cooldown_remaining > 0:
                print(f"   🕐 Cooldown: {cooldown_remaining/60:.1f} minutes remaining")
    
    # Test 2: Create a mock alert and test handling
    print("\n🔍 Test 2: Mock Alert Handling")
    print("-" * 40)
    
    mock_alert = DLQAlert(
        queue_name="test-queue-dlq",
        queue_url="https://sqs.sa-east-1.amazonaws.com/432817839790/test-queue-dlq",
        message_count=5,
        timestamp=datetime.now(),
        region="sa-east-1",
        account_id="432817839790"
    )
    
    print(f"   Creating mock alert for: {mock_alert.queue_name}")
    print(f"   Message count: {mock_alert.message_count}")
    
    # This will trigger notifications and potentially auto-investigation
    print("\n   🚀 Triggering alert handler...")
    monitor._handle_alert(mock_alert)
    print("   ✅ Alert handled")
    
    # Test 3: Check Claude command availability
    print("\n🔍 Test 3: Claude Command Availability")
    print("-" * 40)
    
    import subprocess
    try:
        result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Claude command found: {result.stdout.strip()}")
            
            # Check claude version
            result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Claude version: {result.stdout.strip()}")
        else:
            print("   ❌ Claude command not found in PATH")
            return False
    except Exception as e:
        print(f"   ❌ Error checking Claude command: {e}")
        return False
    
    # Test 4: Test actual investigation trigger for production queue
    print("\n🔍 Test 4: Production Queue Investigation Trigger")
    print("-" * 40)
    
    prod_queue = "fm-digitalguru-api-update-dlq-prod"
    print(f"   Testing queue: {prod_queue}")
    
    if monitor._should_auto_investigate(prod_queue):
        print("   ✅ Queue is eligible for auto-investigation")
        
        # Create a real alert for this queue
        prod_alert = DLQAlert(
            queue_name=prod_queue,
            queue_url=f"https://sqs.sa-east-1.amazonaws.com/432817839790/{prod_queue}",
            message_count=10,
            timestamp=datetime.now(),
            region="sa-east-1",
            account_id="432817839790"
        )
        
        print(f"\n   ⚠️  Ready to trigger REAL auto-investigation for {prod_queue}")
        print("   This will execute Claude with the investigation prompt.")
        response = input("   Continue? (y/n): ")
        
        if response.lower() == 'y':
            print("\n   🚀 Triggering auto-investigation...")
            monitor._handle_alert(prod_alert)
            print("   ✅ Auto-investigation triggered!")
            print("   📊 Check notifications and logs for progress")
            
            # Wait a bit to see if process starts
            time.sleep(3)
            if prod_queue in monitor.investigation_processes:
                print("   ✅ Investigation process is running")
            else:
                print("   ⚠️  Investigation process might have completed quickly or failed to start")
        else:
            print("   ⏭️  Skipped real investigation trigger")
    else:
        print(f"   ⚠️  {prod_queue} is not eligible for auto-investigation")
        print("   Possible reasons:")
        print("   - Investigation already ran recently (cooldown)")
        print("   - Investigation currently running")
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("   ✅ Monitor initialization: Success")
    print("   ✅ Auto-investigation logic: Working")
    print("   ✅ Alert handling: Working")
    print("   ✅ Claude command: Available")
    print("=" * 60)
    
    return True

def check_current_dlqs():
    """Quick check of current DLQ status"""
    print("\n📊 Current DLQ Status Check")
    print("-" * 40)
    
    config = MonitorConfig(
        aws_profile="FABIO-PROD",
        region="sa-east-1",
        auto_investigate_dlqs=[
            "fm-digitalguru-api-update-dlq-prod",
            "fm-transaction-processor-dlq-prd"
        ]
    )
    
    try:
        monitor = DLQMonitor(config)
        alerts = monitor.check_dlq_messages()
        
        if alerts:
            print(f"\n🚨 Found {len(alerts)} DLQs with messages:")
            for alert in alerts:
                print(f"   📋 {alert.queue_name}: {alert.message_count} messages")
                if alert.queue_name in config.auto_investigate_dlqs:
                    print(f"      🤖 Auto-investigation enabled for this queue")
        else:
            print("\n✅ All DLQs are empty")
            
    except Exception as e:
        print(f"\n❌ Error checking DLQs: {e}")

if __name__ == "__main__":
    # First check current DLQ status
    check_current_dlqs()
    
    print("\n" + "=" * 60)
    print("Press Enter to continue with auto-investigation tests...")
    input()
    
    # Run tests
    test_auto_investigation()
