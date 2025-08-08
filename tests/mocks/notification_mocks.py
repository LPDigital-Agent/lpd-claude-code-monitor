"""Mock notification services for testing."""

from typing import Dict, Any, Optional
from unittest.mock import Mock
import subprocess


class MockElevenLabsClient:
    """Mock ElevenLabs TTS client for testing."""
    
    def __init__(self, api_key: str = "test_api_key"):
        self.api_key = api_key
        self.voices = {
            "alice": "voice_001",
            "bob": "voice_002", 
            "charlie": "voice_003"
        }
    
    def generate(self, text: str, voice: str = "alice", model: str = "eleven_monolingual_v1") -> bytes:
        """Mock audio generation."""
        # Return fake audio data
        return b"fake_audio_data_for_" + text.encode()[:50]
    
    def get_voices(self) -> Dict[str, Any]:
        """Mock get_voices method."""
        return {
            "voices": [
                {"voice_id": "voice_001", "name": "Alice", "category": "premade"},
                {"voice_id": "voice_002", "name": "Bob", "category": "premade"},
                {"voice_id": "voice_003", "name": "Charlie", "category": "cloned"}
            ]
        }


class MockMacOSNotification:
    """Mock macOS notification system."""
    
    def __init__(self):
        self.sent_notifications = []
    
    def send_notification(self, title: str, message: str, sound: str = "default") -> bool:
        """Mock sending macOS notification."""
        notification = {
            "title": title,
            "message": message,
            "sound": sound,
            "timestamp": "2024-01-01T10:00:00Z"
        }
        self.sent_notifications.append(notification)
        return True
    
    def get_last_notification(self) -> Optional[Dict[str, str]]:
        """Get the last sent notification."""
        return self.sent_notifications[-1] if self.sent_notifications else None


class MockAudioPlayer:
    """Mock audio player for testing."""
    
    def __init__(self):
        self.played_audio = []
        self.is_playing = False
    
    def play(self, audio_data: bytes, voice: str = "default") -> bool:
        """Mock audio playback."""
        self.played_audio.append({
            "data": audio_data,
            "voice": voice,
            "duration": len(audio_data) / 1000  # Fake duration calculation
        })
        self.is_playing = True
        return True
    
    def stop(self) -> bool:
        """Mock stopping audio playback."""
        self.is_playing = False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get player status."""
        return {
            "is_playing": self.is_playing,
            "tracks_played": len(self.played_audio),
            "last_track": self.played_audio[-1] if self.played_audio else None
        }


class MockSlackClient:
    """Mock Slack client for testing."""
    
    def __init__(self, token: str = "xoxb-test-token"):
        self.token = token
        self.sent_messages = []
    
    def send_message(self, channel: str, text: str, attachments: list = None) -> Dict[str, Any]:
        """Mock sending Slack message."""
        message = {
            "channel": channel,
            "text": text,
            "attachments": attachments or [],
            "timestamp": "1704110400.123456",
            "ok": True
        }
        self.sent_messages.append(message)
        return message
    
    def get_channels(self) -> list:
        """Mock getting Slack channels."""
        return [
            {"id": "C1234567890", "name": "alerts"},
            {"id": "C0987654321", "name": "monitoring"},
            {"id": "C1122334455", "name": "general"}
        ]


class MockEmailSender:
    """Mock email sender for testing."""
    
    def __init__(self, smtp_server: str = "smtp.test.com", port: int = 587):
        self.smtp_server = smtp_server
        self.port = port
        self.sent_emails = []
    
    def send_email(self, to: str, subject: str, body: str, from_addr: str = "noreply@test.com") -> bool:
        """Mock sending email."""
        email = {
            "to": to,
            "from": from_addr,
            "subject": subject,
            "body": body,
            "timestamp": "2024-01-01T10:00:00Z"
        }
        self.sent_emails.append(email)
        return True
    
    def get_sent_count(self) -> int:
        """Get count of sent emails."""
        return len(self.sent_emails)