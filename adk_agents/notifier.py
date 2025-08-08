"""
Notification Agent - Handles all notifications (audio, visual, PR reminders)
"""

from google.adk.agents import LlmAgent
from google.adk.tools import Tool
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import subprocess
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

# Track PR reminders
pr_reminder_state = {
    "tracked_prs": {},
    "last_reminder": {},
    "reminder_interval": timedelta(minutes=10)
}

def create_macos_notification_tool() -> Tool:
    """
    Create a tool for macOS notifications
    """
    async def send_macos_notification(title: str, message: str, sound: bool = True) -> Dict:
        """Send macOS notification"""
        try:
            # Send visual notification
            cmd = [
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Play sound if requested
            if sound:
                subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
            
            return {'success': True, 'type': 'macos'}
            
        except Exception as e:
            logger.error(f"Error sending macOS notification: {e}")
            return {'success': False, 'error': str(e)}
    
    return Tool(
        name="send_macos_notification",
        description="Send macOS notification",
        function=send_macos_notification
    )

def create_voice_notification_tool() -> Tool:
    """
    Create a tool for voice notifications using ElevenLabs
    """
    async def send_voice_notification(message: str, urgency: str = "normal") -> Dict:
        """Send voice notification using ElevenLabs TTS"""
        try:
            # Try ElevenLabs first
            from elevenlabs import generate, play, set_api_key
            
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if api_key:
                set_api_key(api_key)
                
                # Generate and play audio
                audio = generate(
                    text=message,
                    voice="Rachel",  # Or your preferred voice
                    model="eleven_monolingual_v1"
                )
                play(audio)
                
                return {'success': True, 'type': 'elevenlabs'}
            else:
                # Fallback to macOS say command
                subprocess.run(
                    ["say", "-v", "Samantha", message],
                    check=True
                )
                return {'success': True, 'type': 'macos_say'}
                
        except ImportError:
            # ElevenLabs not installed, use macOS say
            try:
                subprocess.run(
                    ["say", "-v", "Samantha", message],
                    check=True
                )
                return {'success': True, 'type': 'macos_say'}
            except Exception as e:
                logger.error(f"Error with voice notification: {e}")
                return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error sending voice notification: {e}")
            return {'success': False, 'error': str(e)}
    
    return Tool(
        name="send_voice_notification",
        description="Send voice notification",
        function=send_voice_notification
    )

def create_pr_reminder_tool() -> Tool:
    """
    Create a tool for PR reminders
    """
    async def send_pr_reminder(pr_number: int, pr_title: str, pr_url: str) -> Dict:
        """Send PR review reminder"""
        try:
            current_time = datetime.now()
            pr_key = f"PR-{pr_number}"
            
            # Check if we should send a reminder
            if pr_key in pr_reminder_state["last_reminder"]:
                last_reminder = pr_reminder_state["last_reminder"][pr_key]
                if current_time - last_reminder < pr_reminder_state["reminder_interval"]:
                    return {'success': False, 'reason': 'Too soon for reminder'}
            
            # Send voice reminder
            message = f"Attention: Pull request number {pr_number} needs review. {pr_title}"
            
            # Send both voice and visual notification
            await send_voice_notification(message, urgency="high")
            await send_macos_notification(
                f"🔔 PR #{pr_number} Review Needed",
                f"{pr_title}\n{pr_url}",
                sound=True
            )
            
            # Update reminder state
            pr_reminder_state["last_reminder"][pr_key] = current_time
            
            return {'success': True, 'pr_number': pr_number}
            
        except Exception as e:
            logger.error(f"Error sending PR reminder: {e}")
            return {'success': False, 'error': str(e)}
    
    return Tool(
        name="send_pr_reminder",
        description="Send PR review reminder",
        function=send_pr_reminder
    )

def create_notifier_agent() -> LlmAgent:
    """
    Create the Notification agent
    """
    
    notifier = LlmAgent(
        name="notifier",
        model="gemini-2.0-flash",
        description="Handles all notifications (audio, visual, PR reminders)",
        instruction="""
        You are the Notification Agent responsible for all alerts and reminders.
        
        NOTIFICATION TYPES:
        
        1. DLQ ALERTS:
           Critical (> 10 messages):
           - Title: "🚨 CRITICAL DLQ ALERT - {queue_name}"
           - Voice: "Critical alert! {queue_name} has {count} messages in dead letter queue"
           - Sound: Yes (urgent)
           
           Warning (1-10 messages):
           - Title: "⚠️ DLQ Warning - {queue_name}"
           - Voice: "Warning: {queue_name} has {count} messages"
           - Sound: Yes (normal)
        
        2. INVESTIGATION STATUS:
           Started:
           - Title: "🔍 Investigation Started"
           - Message: "Analyzing {queue_name} - {message_count} messages"
           - Voice: "Starting automated investigation for {queue_name}"
           
           Completed:
           - Title: "✅ Investigation Complete"
           - Message: "Root cause: {root_cause}"
           - Voice: "Investigation complete. Root cause identified: {root_cause}"
           
           Failed:
           - Title: "❌ Investigation Failed"
           - Message: "Error: {error_message}"
           - Voice: "Investigation failed. Manual intervention required."
        
        3. CODE FIX STATUS:
           Fix Applied:
           - Title: "🛠️ Fix Applied"
           - Message: "Fixed {component} - {fix_type}"
           - Voice: "Code fix applied successfully"
           
           Tests Passed:
           - Title: "✅ Tests Passed"
           - Message: "All tests passing after fix"
           - Voice: "All tests passed. Fix verified."
        
        4. PR NOTIFICATIONS:
           PR Created:
           - Title: "📝 PR Created - #{pr_number}"
           - Message: "{pr_title}"
           - Voice: "Pull request {pr_number} created for review"
           
           PR Review Reminder (every 10 minutes):
           - Title: "🔔 PR Review Needed - #{pr_number}"
           - Message: "Waiting for review: {pr_title}"
           - Voice: "Reminder: Pull request {pr_number} needs review"
           
           PR Approved:
           - Title: "✅ PR Approved - #{pr_number}"
           - Message: "Ready to merge"
           - Voice: "Pull request {pr_number} approved and ready to merge"
        
        5. SYSTEM STATUS:
           Monitor Started:
           - Title: "🚀 ADK Monitor Started"
           - Message: "Monitoring FABIO-PROD DLQs"
           - Voice: "DLQ monitor system started"
           
           Error Detected:
           - Title: "⚠️ System Error"
           - Message: "{error_description}"
           - Voice: "System error detected: {error_description}"
        
        NOTIFICATION CHANNELS:
        
        1. macOS Notifications:
           - Visual alerts in Notification Center
           - System sounds for urgency
        
        2. Voice Notifications:
           - ElevenLabs TTS (if configured)
           - Fallback to macOS say command
           - Different voices for urgency levels
        
        3. PR Audio Reminders:
           - Every 10 minutes for open PRs
           - Stop after PR is merged or closed
           - Priority for auto-investigation PRs
        
        URGENCY LEVELS:
        - CRITICAL: DLQ > 10 messages, system failures
        - HIGH: DLQ 1-10 messages, PR reminders
        - NORMAL: Status updates, completions
        - LOW: Informational messages
        
        SMART FEATURES:
        - Batch similar notifications
        - Prevent notification spam
        - Respect quiet hours (if configured)
        - Track reminder history
        - Escalate if no response
        
        Remember: Clear, timely notifications enable quick response.
        Balance urgency with avoiding notification fatigue.
        """,
        tools=[
            create_macos_notification_tool(),
            create_voice_notification_tool(),
            create_pr_reminder_tool()
        ]
    )
    
    return notifier

def format_notification_message(notification_type: str, data: Dict) -> tuple[str, str]:
    """
    Format notification title and message based on type
    """
    if notification_type == "dlq_alert":
        severity = "CRITICAL" if data['message_count'] > 10 else "Warning"
        emoji = "🚨" if severity == "CRITICAL" else "⚠️"
        title = f"{emoji} DLQ {severity} - {data['queue_name']}"
        message = f"{data['message_count']} messages detected in {data['queue_name']}"
        
    elif notification_type == "investigation_started":
        title = "🔍 Investigation Started"
        message = f"Analyzing {data['queue_name']} - {data['message_count']} messages"
        
    elif notification_type == "investigation_complete":
        title = "✅ Investigation Complete"
        message = f"Root cause: {data.get('root_cause', 'Unknown')}"
        
    elif notification_type == "pr_created":
        title = f"📝 PR Created - #{data['pr_number']}"
        message = data['pr_title']
        
    elif notification_type == "pr_reminder":
        title = f"🔔 PR Review Needed - #{data['pr_number']}"
        message = f"Waiting for review: {data['pr_title']}"
        
    else:
        title = "📢 Notification"
        message = str(data)
    
    return title, message

# Export the notifier
notifier = create_notifier_agent()