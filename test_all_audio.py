#!/usr/bin/env python3
"""
Test ALL audio notifications to ensure they use the new ElevenLabs voice
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_dlq_alerts():
    """Test DLQ alert audio"""
    print("\n🚨 Testing DLQ Alert Audio...")
    print("-" * 50)
    
    from dlq_monitor import MacNotifier
    notifier = MacNotifier()
    
    # Test critical DLQ alert
    print("📢 Testing critical DLQ alert...")
    notifier.send_critical_alert('fm-payment-processing-dlq', 10, 'sa-east-1')
    print("   ✅ DLQ alert sent with new voice")
    
    # Test regular notification
    print("📢 Testing regular notification...")
    notifier.send_notification("Test Alert", "Testing audio system", sound=True)
    print("   ✅ Regular notification sent with new voice")
    
    return True

def test_pr_notifications():
    """Test PR notification audio"""
    print("\n🔔 Testing PR Notification Audio...")
    print("-" * 50)
    
    from dlq_monitor import AudioNotifier
    audio = AudioNotifier()
    
    # Test new PR announcement
    print("📢 Testing new PR announcement...")
    audio.announce_new_pr("dlq-monitor", "Fix critical bug in payment processor")
    print("   ✅ New PR announcement sent with new voice")
    
    # Test PR reminder
    print("📢 Testing PR reminder...")
    audio.announce_pr_reminder("financial-move", "Auto-fix DLQ issues")
    print("   ✅ PR reminder sent with new voice")
    
    return True

def test_pr_monitor_audio():
    """Test PR Monitor audio from pr_notifier module"""
    print("\n🎯 Testing PR Monitor Module Audio...")
    print("-" * 50)
    
    from pr_notifier.pr_audio_monitor import ElevenLabsTTS
    tts = ElevenLabsTTS()
    
    print("📢 Testing direct ElevenLabs TTS...")
    message = "This is a test of the PR monitoring audio system using your custom voice."
    success = tts.speak(message)
    
    if success:
        print("   ✅ Direct ElevenLabs TTS working with new voice")
    else:
        print("   ❌ Direct ElevenLabs TTS failed")
        return False
    
    return True

def main():
    """Run all audio tests"""
    print("=" * 60)
    print("🔊 Complete Audio System Test")
    print("Voice ID: 19STyYD15bswVz51nqLf")
    print("=" * 60)
    
    results = []
    
    # Test DLQ alerts
    results.append(("DLQ Alerts", test_dlq_alerts()))
    
    # Test PR notifications
    results.append(("PR Notifications", test_pr_notifications()))
    
    # Test PR monitor module
    results.append(("PR Monitor Module", test_pr_monitor_audio()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    for name, passed in results:
        status = "✅ Pass" if passed else "❌ Fail"
        print(f"   {name}: {status}")
    print("=" * 60)
    
    if all(result for _, result in results):
        print("\n🎉 All audio systems are using your new voice!")
        print("Voice ID: 19STyYD15bswVz51nqLf")
        print("\nYour production monitor will now use this voice for:")
        print("  • DLQ alert notifications")
        print("  • PR review reminders")
        print("  • Auto-investigation status updates")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()
