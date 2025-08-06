#!/usr/bin/env python3
"""
PR Audio Notification Module for DLQ Monitor
Monitors GitHub PRs created by auto-investigation and sends audio notifications
"""

import os
import time
import json
import subprocess
import threading
import logging
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Try importing pygame, but don't fail if not available
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logging.warning("pygame not available - audio notifications will be disabled")

logger = logging.getLogger(__name__)

# ElevenLabs Configuration
ELEVENLABS_API_KEY = "sk_2e4f9bf2d246b7c1a087ab8bdefdd818f2561639e2e360eb"
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
VOICE_ID = "19STyYD15bswVz51nqLf"  # Your custom voice selection

@dataclass
class PullRequest:
    """Represents a Pull Request that needs review"""
    pr_id: int
    repo_name: str
    title: str
    author: str
    url: str
    created_at: datetime
    updated_at: datetime
    is_draft: bool = False
    is_auto_investigation: bool = False
    last_notification: Optional[datetime] = None
    notification_count: int = 0

    def __hash__(self):
        return hash((self.repo_name, self.pr_id))

    def __eq__(self, other):
        if not isinstance(other, PullRequest):
            return False
        return self.repo_name == other.repo_name and self.pr_id == other.pr_id


class ElevenLabsTTS:
    """Handle text-to-speech using ElevenLabs API"""
    
    def __init__(self, api_key: str = ELEVENLABS_API_KEY, voice_id: str = VOICE_ID):
        self.api_key = api_key
        self.voice_id = voice_id
        self.api_url = f"{ELEVENLABS_API_URL}/{voice_id}"
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
        
    def generate_audio(self, text: str) -> Optional[bytes]:
        """Generate audio from text using ElevenLabs API"""
        if not PYGAME_AVAILABLE:
            return None
            
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        try:
            response = requests.post(self.api_url, json=data, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"ElevenLabs API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            return None
    
    def play_audio(self, audio_data: bytes):
        """Play audio data"""
        if not PYGAME_AVAILABLE:
            return
            
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
    
    def speak(self, text: str) -> bool:
        """Generate and play speech"""
        if not PYGAME_AVAILABLE:
            logger.warning("Audio notifications disabled - pygame not available")
            return False
            
        audio_data = self.generate_audio(text)
        if audio_data:
            self.play_audio(audio_data)
            return True
        return False


class GitHubPRMonitor:
    """Monitor GitHub for PRs that need review"""
    
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def get_automation_prs(self) -> List[PullRequest]:
        """Get PRs created by automation (including DLQ auto-investigation)"""
        prs = []
        automation_patterns = [
            "Auto-fix", "DLQ Investigation", "Automated Fix", 
            "Auto-investigation", "Fix DLQ", "Dead Letter Queue",
            "fm-digitalguru", "fm-transaction-processor"
        ]
        
        for pattern in automation_patterns:
            query = f'is:pr is:open "{pattern}" in:title user:{self.username}'
            url = f"https://api.github.com/search/issues?q={query}&sort=created&order=desc"
            
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("items", []):
                        pr = self._parse_pr(item, is_auto=True)
                        if pr and pr not in prs:
                            prs.append(pr)
            except Exception as e:
                logger.error(f"Failed to fetch automation PRs: {e}")
        
        # Also check PRs where user is requested reviewer
        try:
            query = f"is:pr is:open review-requested:{self.username}"
            url = f"https://api.github.com/search/issues?q={query}&sort=created&order=desc"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    pr = self._parse_pr(item, is_auto=False)
                    if pr and pr not in prs:
                        # Check if it's actually an automation PR
                        if any(pattern in pr.title for pattern in automation_patterns):
                            pr.is_auto_investigation = True
                        prs.append(pr)
        except Exception as e:
            logger.error(f"Failed to fetch review requests: {e}")
        
        return prs
    
    def _parse_pr(self, data: dict, is_auto: bool = False) -> Optional[PullRequest]:
        """Parse PR data from search API"""
        try:
            repo_url = data.get("repository_url", "")
            repo_name = "/".join(repo_url.split("/")[-2:]) if repo_url else "unknown"
            
            return PullRequest(
                pr_id=data["number"],
                repo_name=repo_name,
                title=data["title"],
                author=data["user"]["login"],
                url=data["html_url"],
                created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                is_draft=data.get("draft", False),
                is_auto_investigation=is_auto
            )
        except Exception as e:
            logger.error(f"Failed to parse PR: {e}")
            return None


class PRAudioMonitor:
    """PR Audio Notification System integrated with DLQ Monitor"""
    
    def __init__(self, github_token: str = None, github_username: str = None, 
                 notification_interval: int = 600, enable_audio: bool = True):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN", "")
        self.github_username = github_username or os.getenv("GITHUB_USERNAME", "fabio.santos")
        self.notification_interval = notification_interval
        self.enable_audio = enable_audio and PYGAME_AVAILABLE
        
        if self.github_token and self.github_username:
            self.tts = ElevenLabsTTS() if self.enable_audio else None
            self.github = GitHubPRMonitor(self.github_token, self.github_username)
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("GitHub credentials not configured - PR monitoring disabled")
        
        self.tracked_prs: Dict[Tuple[str, int], PullRequest] = {}
        self.running = False
        self.thread = None
        self.console = Console()
    
    def generate_notification_message(self, pr: PullRequest) -> str:
        """Generate notification message for a PR"""
        pr_type = "auto-investigation pull request" if pr.is_auto_investigation else "pull request"
        
        messages = [
            f"Attention: There's a {pr_type} waiting for your review.",
            f"Repository: {pr.repo_name.replace('/', ' slash ')}.",
            f"Title: {pr.title}.",
            f"Author: {pr.author}.",
            f"This PR has been open for {self._format_duration(datetime.now() - pr.created_at)}.",
        ]
        
        if pr.notification_count > 0:
            messages.append(f"This is reminder number {pr.notification_count + 1}.")
        
        if pr.is_auto_investigation:
            messages.append("This PR was created by the DLQ auto-investigation system and requires your approval.")
        
        return " ".join(messages)
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration in human-readable format"""
        days = duration.days
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        if not parts:
            return "less than a minute"
        
        return " and ".join(parts)
    
    def notify_pr(self, pr: PullRequest):
        """Send audio notification for a PR"""
        message = self.generate_notification_message(pr)
        
        # Log the notification
        logger.info(f"PR notification: {pr.repo_name} #{pr.pr_id} - {pr.title}")
        
        # Send audio notification if enabled
        if self.enable_audio and self.tts:
            self.tts.speak(message)
        
        # Send Mac notification
        self._send_mac_notification(pr)
        
        pr.last_notification = datetime.now()
        pr.notification_count += 1
    
    def _send_mac_notification(self, pr: PullRequest):
        """Send macOS notification"""
        title = f"🔔 PR Review Required - #{pr.pr_id}"
        message = f"{pr.repo_name}\\n{pr.title}\\nAuthor: {pr.author}"
        
        if pr.is_auto_investigation:
            title = f"🤖 Auto-Investigation PR - #{pr.pr_id}"
        
        try:
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ], check=True, capture_output=True)
        except Exception as e:
            logger.error(f"Failed to send Mac notification: {e}")
    
    def check_prs(self):
        """Check for PRs that need notifications"""
        if not self.enabled:
            return
        
        try:
            # Fetch current PRs
            current_prs = self.github.get_automation_prs()
            
            # Update tracked PRs
            current_keys = {(pr.repo_name, pr.pr_id): pr for pr in current_prs}
            
            # Check for new PRs
            for pr in current_prs:
                key = (pr.repo_name, pr.pr_id)
                if key not in self.tracked_prs:
                    self.tracked_prs[key] = pr
                    logger.info(f"New PR detected: {pr.repo_name} #{pr.pr_id}")
                    # Immediate notification for new PRs
                    self.notify_pr(pr)
                else:
                    # Update existing PR but preserve notification history
                    existing = self.tracked_prs[key]
                    pr.last_notification = existing.last_notification
                    pr.notification_count = existing.notification_count
                    self.tracked_prs[key] = pr
            
            # Check for closed PRs
            for key in list(self.tracked_prs.keys()):
                if key not in current_keys:
                    pr = self.tracked_prs[key]
                    logger.info(f"PR closed/merged: {pr.repo_name} #{pr.pr_id}")
                    if self.enable_audio and self.tts:
                        message = f"Good news! Pull request number {pr.pr_id} in {pr.repo_name.replace('/', ' slash ')} has been closed or merged."
                        self.tts.speak(message)
                    del self.tracked_prs[key]
            
            # Check notification schedule
            now = datetime.now()
            for pr in self.tracked_prs.values():
                if pr.last_notification:
                    time_since = (now - pr.last_notification).total_seconds()
                    if time_since >= self.notification_interval:
                        self.notify_pr(pr)
                        
        except Exception as e:
            logger.error(f"Error checking PRs: {e}")
    
    def get_status_table(self) -> Table:
        """Get status table for display"""
        table = Table(title="🔔 PR Review Status", show_header=True, header_style="bold magenta")
        table.add_column("PR #", style="cyan", no_wrap=True)
        table.add_column("Repository", style="green")
        table.add_column("Title", style="yellow", max_width=40)
        table.add_column("Type", style="blue")
        table.add_column("Notifications", style="red")
        
        for pr in self.tracked_prs.values():
            pr_type = "🤖 Auto" if pr.is_auto_investigation else "👤 Manual"
            table.add_row(
                str(pr.pr_id),
                pr.repo_name,
                pr.title[:37] + "..." if len(pr.title) > 40 else pr.title,
                pr_type,
                str(pr.notification_count)
            )
        
        return table
    
    def start_background_monitoring(self):
        """Start PR monitoring in background thread"""
        if not self.enabled:
            logger.warning("PR monitoring disabled - GitHub credentials not configured")
            return
        
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("PR audio monitoring started in background")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                self.check_prs()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"PR monitoring error: {e}")
                time.sleep(60)
    
    def stop(self):
        """Stop PR monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)


# Export classes for use by other modules
__all__ = ['ElevenLabsTTS', 'PRAudioMonitor', 'PullRequest']
