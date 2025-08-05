#!/usr/bin/env python3
"""Simple notification test without AWS dependencies"""

import subprocess


def test_mac_notification():
    """Test macOS notification system"""
    try:
        cmd = [
            "osascript", "-e",
            'display notification "DLQ Monitor notification test successful!" with title "🚨 DLQ Monitor Test"'
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True)
        print("✅ Mac notification sent successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to send notification: {e}")
        return False
    except FileNotFoundError:
        print("❌ osascript not found - not running on macOS?")
        return False


if __name__ == "__main__":
    print("🧪 Testing macOS notification system...")
    success = test_mac_notification()
    
    if success:
        print("🎉 Notification system is working!")
        print("You should have seen a notification appear on your Mac.")
    else:
        print("💔 Notification system test failed.")
