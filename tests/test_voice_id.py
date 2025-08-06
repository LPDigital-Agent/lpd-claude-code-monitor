#!/usr/bin/env python3
"""
Test to verify ElevenLabs Voice ID configuration
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def test_voice_id():
    """Verify the correct voice ID is configured"""
    
    print("🔍 Checking ElevenLabs Voice ID Configuration...")
    
    try:
        from dlq_monitor.notifiers.pr_audio import VOICE_ID, ElevenLabsTTS
        
        expected_voice_id = "19STyYD15bswVz51nqLf"
        
        # Check the global constant
        if VOICE_ID == expected_voice_id:
            print(f"✅ Global VOICE_ID is correct: {VOICE_ID}")
        else:
            print(f"❌ Global VOICE_ID mismatch!")
            print(f"   Expected: {expected_voice_id}")
            print(f"   Found: {VOICE_ID}")
            return False
        
        # Check the TTS class default
        tts = ElevenLabsTTS()
        if tts.voice_id == expected_voice_id:
            print(f"✅ ElevenLabsTTS voice_id is correct: {tts.voice_id}")
        else:
            print(f"❌ ElevenLabsTTS voice_id mismatch!")
            print(f"   Expected: {expected_voice_id}")
            print(f"   Found: {tts.voice_id}")
            return False
        
        # Check the API URL includes the voice ID
        expected_url = f"https://api.elevenlabs.io/v1/text-to-speech/{expected_voice_id}"
        if tts.api_url == expected_url:
            print(f"✅ API URL is correctly formed with voice ID")
            print(f"   URL: {tts.api_url}")
        else:
            print(f"❌ API URL mismatch!")
            print(f"   Expected: {expected_url}")
            print(f"   Found: {tts.api_url}")
            return False
        
        # Test that MacNotifier uses the same TTS configuration
        from dlq_monitor.notifiers.macos_notifier import MacNotifier
        
        notifier = MacNotifier()
        if notifier.tts and hasattr(notifier.tts, 'voice_id'):
            if notifier.tts.voice_id == expected_voice_id:
                print(f"✅ MacNotifier uses correct voice ID: {notifier.tts.voice_id}")
            else:
                print(f"❌ MacNotifier voice_id mismatch!")
                print(f"   Expected: {expected_voice_id}")
                print(f"   Found: {notifier.tts.voice_id}")
                return False
        else:
            print("⚠️  MacNotifier TTS not initialized (ElevenLabs may not be available)")
        
        print("\n✅ All voice ID configurations are correct!")
        print(f"   Voice ID: {expected_voice_id}")
        print("   This voice will be used for all ElevenLabs notifications")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_voice_id()
    sys.exit(0 if success else 1)