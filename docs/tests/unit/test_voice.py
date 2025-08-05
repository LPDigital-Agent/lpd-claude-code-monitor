#!/usr/bin/env python3
"""
Test the new ElevenLabs voice
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pr_notifier.pr_audio_monitor import ElevenLabsTTS

def test_new_voice():
    """Test the new voice with various notifications"""
    print("🔊 Testing new ElevenLabs voice ID: 19STyYD15bswVz51nqLf")
    print("-" * 50)
    
    tts = ElevenLabsTTS()
    
    # Test messages
    messages = [
        "Hello! This is your new voice for DLQ monitoring notifications.",
        "Dead letter queue alert: payment processing queue has 5 messages.",
        "Attention: There's an auto-investigation pull request waiting for your review.",
        "Good news! All dead letter queues are clear."
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n📢 Test {i}: {message[:50]}...")
        success = tts.speak(message)
        
        if success:
            print("   ✅ Audio played successfully")
        else:
            print("   ❌ Audio playback failed")
            return False
    
    print("\n" + "=" * 50)
    print("✅ All voice tests completed successfully!")
    print("Your new voice is configured and working.")
    return True

if __name__ == "__main__":
    test_new_voice()
