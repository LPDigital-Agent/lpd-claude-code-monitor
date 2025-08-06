#!/usr/bin/env python3
"""
macOS Notification Handler for DLQ Monitor
Implements AWS SQS best practices for notification delivery
"""

import subprocess
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MacNotifier:
    """Handle macOS notifications with prominent queue names"""
    
    def __init__(self):
        """Initialize with ElevenLabs TTS if available"""
        self.tts = None
        try:
            from .pr_audio import ElevenLabsTTS
            self.tts = ElevenLabsTTS()
            logger.info("ElevenLabs TTS initialized")
        except ImportError:
            logger.debug("ElevenLabs TTS not available, using macOS say")
        except Exception as e:
            logger.warning(f"Failed to initialize ElevenLabs: {e}")
    
    def send_notification(self, title: str, message: str, sound: bool = True) -> bool:
        """Send notification via macOS Notification Center
        
        Args:
            title: Notification title
            message: Notification message
            sound: Whether to play sound
            
        Returns:
            True if notification was sent successfully
        """
        try:
            # Send visual notification
            cmd = [
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ]
            subprocess.run(cmd, check=True, capture_output=True, timeout=5)
            
            # Send audio notification if enabled
            if sound:
                if self.tts:
                    # Use ElevenLabs with custom voice
                    try:
                        self.tts.speak("Dead letter queue alert")
                    except Exception as e:
                        logger.debug(f"TTS failed, using fallback: {e}")
                        self._fallback_speech("Dead letter queue alert")
                else:
                    # Fallback to macOS say
                    self._fallback_speech("Dead letter queue alert")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to send notification: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.warning("Notification command timed out")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending notification: {e}")
            return False
    
    def _fallback_speech(self, text: str) -> None:
        """Fallback speech using macOS say command"""
        try:
            subprocess.run(
                ["osascript", "-e", f'say "{text}"'],
                check=False,
                capture_output=True,
                timeout=10
            )
        except Exception:
            pass  # Speech is optional, don't fail
    
    def send_critical_alert(self, queue_name: str, message_count: int, region: str = "sa-east-1") -> bool:
        """Send critical alert with prominent queue name
        
        Args:
            queue_name: Name of the DLQ
            message_count: Number of messages in queue
            region: AWS region
            
        Returns:
            True if alert was sent successfully
        """
        title = f"🚨 DLQ ALERT - {queue_name}"
        message = f"Profile: FABIO-PROD\\nRegion: {region}\\nQueue: {queue_name}\\nMessages: {message_count}"
        
        # Clean queue name for speech
        clean_name = queue_name.replace('-', ' ').replace('_', ' ')
        speech_message = f"Dead letter queue alert for {clean_name} queue. {message_count} messages detected."
        
        # Send visual notification first
        visual_sent = self.send_notification(title, message, sound=False)
        
        # Then send speech notification
        if self.tts:
            try:
                self.tts.speak(speech_message)
            except Exception as e:
                logger.debug(f"TTS failed for critical alert: {e}")
                self._fallback_speech(speech_message)
        else:
            self._fallback_speech(speech_message)
        
        return visual_sent
    
    def send_investigation_notification(self, queue_name: str, status: str, details: Optional[str] = None) -> bool:
        """Send notification about investigation status
        
        Args:
            queue_name: Name of the DLQ
            status: Investigation status (started, completed, failed)
            details: Optional details about the investigation
            
        Returns:
            True if notification was sent successfully
        """
        status_icons = {
            'started': '🔍',
            'completed': '✅',
            'failed': '❌',
            'timeout': '⏰'
        }
        
        icon = status_icons.get(status, '📋')
        title = f"{icon} AUTO-INVESTIGATION {status.upper()}"
        
        message = f"Queue: {queue_name}"
        if details:
            message += f"\\n{details[:100]}"  # Limit details length
        
        return self.send_notification(title, message, sound=True)
    
    def send_pr_notification(self, repo_name: str, pr_title: str, is_new: bool = True) -> bool:
        """Send notification about pull request
        
        Args:
            repo_name: Repository name
            pr_title: Pull request title
            is_new: Whether this is a new PR or reminder
            
        Returns:
            True if notification was sent successfully
        """
        if is_new:
            title = "🎯 New PR Created"
            message = f"Repository: {repo_name}\\nTitle: {pr_title}\\nPlease review and approve."
            speech = f"Pull request created for review in repository {repo_name.replace('-', ' ')}"
        else:
            title = "⏰ PR Review Reminder"
            message = f"Repository: {repo_name}\\nTitle: {pr_title}\\nStill waiting for review."
            speech = f"Reminder: Pull request in {repo_name.replace('-', ' ')} is waiting for review"
        
        # Send visual notification
        visual_sent = self.send_notification(title, message, sound=False)
        
        # Send speech notification
        if self.tts:
            try:
                self.tts.speak(speech)
            except Exception:
                self._fallback_speech(speech)
        else:
            self._fallback_speech(speech)
        
        return visual_sent


# Export the notifier class
__all__ = ['MacNotifier']