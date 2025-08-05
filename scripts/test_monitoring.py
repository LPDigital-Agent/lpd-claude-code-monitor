#!/usr/bin/env python3
"""
Test script to verify DLQ monitoring is working
Demonstrates both original and optimized monitoring
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from dlq_monitor.core.monitor import DLQMonitor, MonitorConfig
from dlq_monitor.core.optimized_monitor import OptimizedDLQMonitor, OptimizedMonitorConfig


def test_original_monitor():
    """Test the original monitor"""
    print("\n" + "="*60)
    print("🔧 Testing Original DLQ Monitor")
    print("="*60)
    
    config = MonitorConfig(
        aws_profile="FABIO-PROD",
        region="sa-east-1",
        check_interval=30,
        notification_sound=False
    )
    
    try:
        monitor = DLQMonitor(config)
        
        # Discover queues
        print("\n📋 Discovering DLQ queues...")
        start_time = time.time()
        dlq_queues = monitor.discover_dlq_queues()
        discovery_time = time.time() - start_time
        
        print(f"✅ Found {len(dlq_queues)} DLQ queues in {discovery_time:.2f} seconds")
        
        if dlq_queues:
            for queue in dlq_queues[:3]:  # Show first 3
                print(f"  - {queue['name']}")
        
        # Check for messages
        print("\n🔍 Checking for messages...")
        start_time = time.time()
        alerts = monitor.check_dlq_messages()
        check_time = time.time() - start_time
        
        print(f"✅ Checked all queues in {check_time:.2f} seconds")
        
        if alerts:
            print(f"⚠️  Found {len(alerts)} queues with messages:")
            for alert in alerts:
                print(f"  - {alert.queue_name}: {alert.message_count} messages")
        else:
            print("✅ All DLQs are empty")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing original monitor: {e}")
        return False


def test_optimized_monitor():
    """Test the optimized monitor with improvements"""
    print("\n" + "="*60)
    print("🚀 Testing Optimized DLQ Monitor")
    print("="*60)
    
    config = OptimizedMonitorConfig(
        aws_profile="FABIO-PROD",
        region="sa-east-1",
        check_interval=30,
        notification_sound=False,
        retrieve_message_samples=False,
        enable_cloudwatch_metrics=False,  # Disable for test
        long_polling_wait_seconds=5  # Shorter for testing
    )
    
    try:
        monitor = OptimizedDLQMonitor(config)
        
        # Discover queues with caching
        print("\n📋 Discovering DLQ queues (with batch operations)...")
        start_time = time.time()
        dlq_queues = monitor.discover_dlq_queues_batch()
        discovery_time = time.time() - start_time
        
        print(f"✅ Found {len(dlq_queues)} DLQ queues in {discovery_time:.2f} seconds")
        
        # Test caching
        print("\n💾 Testing cache (should be instant)...")
        start_time = time.time()
        dlq_queues_cached = monitor.discover_dlq_queues_batch()
        cache_time = time.time() - start_time
        
        print(f"✅ Retrieved from cache in {cache_time:.4f} seconds")
        
        # Check for messages with optimization
        print("\n🔍 Checking for messages (concurrent operations)...")
        start_time = time.time()
        alerts = monitor.check_dlq_messages_optimized()
        check_time = time.time() - start_time
        
        print(f"✅ Checked all queues in {check_time:.2f} seconds")
        
        if alerts:
            print(f"⚠️  Found {len(alerts)} queues with messages:")
            for alert in alerts:
                print(f"  - {alert.queue_name}: {alert.message_count} messages")
        else:
            print("✅ All DLQs are empty")
        
        # Health check
        print("\n🏥 Performing health check...")
        health = monitor.health_check()
        print(f"✅ Status: {health['status']}")
        print(f"  - SQS: {health['checks'].get('sqs', 'unknown')}")
        print(f"  - Cache size: {health['checks'].get('cache_size', 0)}")
        print(f"  - Thread pool: {health['checks'].get('thread_pool', {})}")
        
        # Cleanup
        monitor.cleanup()
        print("\n🧹 Cleaned up resources")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing optimized monitor: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_performance():
    """Compare performance between original and optimized"""
    print("\n" + "="*60)
    print("📊 Performance Comparison")
    print("="*60)
    
    # Test original
    print("\n1️⃣ Original Monitor Performance:")
    original_start = time.time()
    original_success = test_original_monitor()
    original_time = time.time() - original_start
    
    # Test optimized
    print("\n2️⃣ Optimized Monitor Performance:")
    optimized_start = time.time()
    optimized_success = test_optimized_monitor()
    optimized_time = time.time() - optimized_start
    
    # Summary
    print("\n" + "="*60)
    print("📈 Performance Summary")
    print("="*60)
    
    print(f"\n⏱️  Original Monitor:")
    print(f"  - Status: {'✅ Success' if original_success else '❌ Failed'}")
    print(f"  - Total time: {original_time:.2f} seconds")
    
    print(f"\n⚡ Optimized Monitor:")
    print(f"  - Status: {'✅ Success' if optimized_success else '❌ Failed'}")
    print(f"  - Total time: {optimized_time:.2f} seconds")
    
    if original_success and optimized_success:
        improvement = ((original_time - optimized_time) / original_time) * 100
        print(f"\n🎯 Performance Improvement: {improvement:.1f}%")
        
        print("\n✨ Key Improvements:")
        print("  - 🔄 Connection pooling reduces overhead")
        print("  - 💾 Caching eliminates redundant API calls")
        print("  - 🚀 Concurrent operations speed up checking")
        print("  - 📦 Batch operations process more efficiently")
        print("  - ⏰ Long polling reduces empty responses")


def main():
    """Main test function"""
    print("🔬 DLQ Monitor Test Suite")
    print("Testing monitoring functionality and optimizations")
    
    # Check if we can import
    try:
        import boto3
        print("✅ AWS SDK (boto3) available")
    except ImportError:
        print("❌ boto3 not installed. Run: pip install boto3")
        sys.exit(1)
    
    # Run comparison
    compare_performance()
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    main()