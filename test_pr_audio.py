#!/usr/bin/env python3
"""
Test PR Audio Notification System
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pr_notifier.pr_audio_monitor import ElevenLabsTTS, GitHubPRMonitor, PRAudioMonitor

def test_audio():
    """Test audio generation and playback"""
    print("🔊 Testing Audio System...")
    tts = ElevenLabsTTS()
    
    message = "Testing audio notifications. This is a test of the PR review notification system."
    success = tts.speak(message)
    
    if success:
        print("✅ Audio test successful!")
    else:
        print("❌ Audio test failed - check ElevenLabs API key")
    
    return success

def test_github():
    """Test GitHub connection"""
    print("\n🔍 Testing GitHub Connection...")
    
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME", "fabio.santos")
    
    if not token:
        print("❌ GITHUB_TOKEN not set")
        print("💡 Set it with: export GITHUB_TOKEN='your_token'")
        return False
    
    print(f"✅ GitHub Token: Found")
    print(f"✅ GitHub Username: {username}")
    
    monitor = GitHubPRMonitor(token, username)
    
    try:
        prs = monitor.get_automation_prs()
        print(f"✅ Found {len(prs)} automation PRs")
        
        for pr in prs[:3]:  # Show first 3
            print(f"   • PR #{pr.pr_id} in {pr.repo_name}: {pr.title[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ GitHub test failed: {e}")
        return False

def test_full_system():
    """Test the full PR monitoring system"""
    print("\n🚀 Testing Full PR Monitoring System...")
    
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME", "fabio.santos")
    
    if not token:
        print("❌ Cannot test - GITHUB_TOKEN not set")
        return False
    
    pr_monitor = PRAudioMonitor(
        github_token=token,
        github_username=username,
        notification_interval=60,  # 1 minute for testing
        enable_audio=True
    )
    
    if not pr_monitor.enabled:
        print("❌ PR Monitor not enabled")
        return False
    
    print("✅ PR Monitor initialized")
    print("🔍 Checking for PRs...")
    
    pr_monitor.check_prs()
    
    if pr_monitor.tracked_prs:
        print(f"✅ Tracking {len(pr_monitor.tracked_prs)} PRs")
        
        # Test notification for first PR
        first_pr = list(pr_monitor.tracked_prs.values())[0]
        print(f"\n🔔 Sending test notification for PR #{first_pr.pr_id}...")
        pr_monitor.notify_pr(first_pr)
        print("✅ Notification sent!")
    else:
        print("ℹ️  No PRs currently need review")
        
        # Send a test notification anyway
        print("\n🔔 Sending test audio notification...")
        if pr_monitor.tts:
            success = pr_monitor.tts.speak(
                "PR audio notification system is working correctly. "
                "You will receive audio notifications when pull requests need your review."
            )
            if success:
                print("✅ Test notification sent!")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 PR Audio Notification System Test")
    print("=" * 60)
    
    # Test audio
    audio_ok = test_audio()
    
    # Test GitHub
    github_ok = test_github()
    
    # Test full system
    if audio_ok and github_ok:
        full_ok = test_full_system()
    else:
        print("\n⚠️  Skipping full system test due to previous failures")
        full_ok = False
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Audio System: {'✅ Pass' if audio_ok else '❌ Fail'}")
    print(f"   GitHub Connection: {'✅ Pass' if github_ok else '❌ Fail'}")
    print(f"   Full System: {'✅ Pass' if full_ok else '❌ Fail'}")
    print("=" * 60)
    
    if audio_ok and github_ok and full_ok:
        print("\n🎉 All tests passed! System is ready for use.")
        print("\n🚀 Start monitoring with: ./start_monitor.sh production")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()
