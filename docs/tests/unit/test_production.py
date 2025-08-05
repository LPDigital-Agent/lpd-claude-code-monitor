#!/usr/bin/env python3
"""
Quick Test of Production DLQ Monitor - Limited Cycles
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from dlq_monitor import DLQMonitor, MonitorConfig

def test_production_monitoring():
    """Run a few cycles of production monitoring"""
    print("🎯 Testing REAL Production DLQ Monitoring")
    print("📋 Profile: FABIO-PROD")  
    print("🌍 Region: sa-east-1")
    print("⏱️  Running 3 monitoring cycles...")
    print("=" * 60)
    
    config = MonitorConfig(
        aws_profile="FABIO-PROD",
        region="sa-east-1", 
        check_interval=5,  # Faster for testing
        notification_sound=True
    )
    
    try:
        monitor = DLQMonitor(config)
        
        # Run limited cycles
        for cycle in range(3):
            print(f"\n🔄 Cycle {cycle + 1}/3")
            alerts = monitor.check_dlq_messages()
            
            if alerts:
                print(f"🚨 REAL ALERTS FOUND: {len(alerts)} DLQ(s) with messages!")
                for alert in alerts:
                    print(f"   📋 {alert.queue_name}: {alert.message_count} messages")
            else:
                print("✅ All DLQs are currently empty")
            
            if cycle < 2:  # Don't wait after last cycle
                print(f"⏳ Waiting 5 seconds...")
                import time
                time.sleep(5)
        
        print("\n🏁 Production test completed!")
        print("💡 To run continuous monitoring: ./run_production.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Check AWS credentials: aws configure list --profile FABIO-PROD")

if __name__ == "__main__":
    test_production_monitoring()
