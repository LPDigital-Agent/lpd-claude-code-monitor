#!/usr/bin/env python3
"""
Voice notification check module
Ensures voice notifications respect the mute state
"""
import os
import logging

logger = logging.getLogger(__name__)

def is_voice_enabled() -> bool:
    """Check if voice notifications are enabled"""
    # Check environment variable
    voice_env = os.environ.get('VOICE_NOTIFICATIONS_ENABLED', 'True')
    
    # Check if explicitly disabled
    if voice_env.lower() in ['false', '0', 'no', 'off']:
        logger.info("Voice notifications are muted")
        return False
    
    return True

def should_play_audio() -> bool:
    """Determine if audio should play based on settings"""
    # Check voice enabled state
    if not is_voice_enabled():
        return False
    
    # Check if in quiet hours (optional future feature)
    # from datetime import datetime
    # now = datetime.now()
    # if now.hour >= 22 or now.hour < 8:  # Quiet hours 10pm - 8am
    #     return False
    
    return True

class VoiceGuard:
    """Context manager to ensure voice respects mute state"""
    
    def __init__(self):
        self.enabled = is_voice_enabled()
    
    def __enter__(self):
        return self.enabled
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# Usage example:
# with VoiceGuard() as voice_allowed:
#     if voice_allowed:
#         play_audio()