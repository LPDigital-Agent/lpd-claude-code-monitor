"""
Notifiers Module

This module provides notification capabilities for the DLQ monitoring system.
It supports multiple notification channels including audio alerts using ElevenLabs TTS,
GitHub PR monitoring, and various alert mechanisms.

Key Features:
- ElevenLabs Text-to-Speech integration for audio notifications
- GitHub PR monitoring with automated reminders
- Pull request audio notifications for pending reviews  
- Customizable voice and notification settings
- Integration with macOS native notifications

Notification Types:
- Audio alerts for new DLQ messages
- Voice notifications for PR status changes
- Automated PR review reminders
- Real-time status updates
"""

# Lazy imports to avoid dependency issues
def __getattr__(name):
    """Lazy import implementation."""
    if name in ["PullRequest", "ElevenLabsTTS", "GitHubPRMonitor", "PRAudioMonitor"]:
        from .pr_audio import (
            PullRequest, ElevenLabsTTS, GitHubPRMonitor, PRAudioMonitor
        )
        return locals()[name]
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Data structures
    "PullRequest",
    
    # Audio/TTS services
    "ElevenLabsTTS",
    
    # PR monitoring
    "GitHubPRMonitor",
    "PRAudioMonitor",
]