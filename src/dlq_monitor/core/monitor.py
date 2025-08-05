#!/usr/bin/env python3
"""
AWS SQS Dead Letter Queue Monitor - Enhanced for FABIO-PROD
Monitors all DLQs in FABIO-PROD profile (sa-east-1) and sends Mac notifications with queue names
"""

import boto3
import time
import logging
import json
import subprocess
import os
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
from botocore.exceptions import ClientError, NoCredentialsError


@dataclass
class DLQAlert:
    queue_name: str
    queue_url: str
    message_count: int
    timestamp: datetime
    region: str
    account_id: str
    
    
@dataclass
class MonitorConfig:
    aws_profile: str = "FABIO-PROD"
    region: str = "sa-east-1"
    check_interval: int = 30  # seconds
    dlq_patterns: List[str] = None
    notification_sound: bool = True
    auto_investigate_dlqs: List[str] = None  # DLQs that trigger auto-investigation
    claude_command_timeout: int = 1800  # 30 minutes for Claude investigation
    
    # PR Monitoring Configuration
    enable_pr_monitoring: bool = True
    pr_reminder_interval: int = 600  # 10 minutes in seconds
    pr_automation_authors: List[str] = None  # Authors that indicate automation PRs
    pr_title_patterns: List[str] = None  # Title patterns to identify automation PRs
    
    def __post_init__(self):
        if self.dlq_patterns is None:
            self.dlq_patterns = ["-dlq", "-dead-letter", "-deadletter", "_dlq", "-dl"]
        if self.auto_investigate_dlqs is None:
            self.auto_investigate_dlqs = ["fm-digitalguru-api-update-dlq-prod"]
        if self.pr_automation_authors is None:
            self.pr_automation_authors = ["github-actions[bot]", "github-actions", "dependabot[bot]"]
        if self.pr_title_patterns is None:
            self.pr_title_patterns = ["Auto-fix", "DLQ Investigation", "Automated Fix", "Auto-investigation", "Fix DLQ"]


class MacNotifier:
    """Handle macOS notifications with prominent queue names"""
    
    def __init__(self):
        """Initialize with ElevenLabs TTS if available"""
        self.tts = None
        try:
            from pr_notifier.pr_audio_monitor import ElevenLabsTTS
            self.tts = ElevenLabsTTS()
        except ImportError:
            pass  # Will use macOS say as fallback
    
    def send_notification(self, title: str, message: str, sound: bool = True) -> bool:
        """Send notification via macOS Notification Center"""
        try:
            # Send visual notification
            cmd = [
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Send audio notification if enabled
            if sound:
                if self.tts:
                    # Use ElevenLabs with custom voice
                    self.tts.speak("Dead letter queue alert")
                else:
                    # Fallback to macOS say
                    subprocess.run([
                        "osascript", "-e", 'say "Dead letter queue alert"'
                    ], check=True, capture_output=True)
            
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to send notification: {e}")
            return False
    
    def send_critical_alert(self, queue_name: str, message_count: int, region: str = "sa-east-1") -> bool:
        """Send critical alert with prominent queue name"""
        title = f"🚨 DLQ ALERT - {queue_name}"
        message = f"Profile: FABIO-PROD\\nRegion: {region}\\nQueue: {queue_name}\\nMessages: {message_count}"
        
        # Announce the queue name via speech
        speech_message = f"Dead letter queue alert for {queue_name.replace('-', ' ')} queue. {message_count} messages detected."
        
        if self.tts:
            # Use ElevenLabs with custom voice
            try:
                self.tts.speak(speech_message)
            except:
                pass  # Speech is optional
        else:
            # Fallback to macOS say
            try:
                subprocess.run([
                    "osascript", "-e",
                    f'say "{speech_message}"'
                ], check=True, capture_output=True)
            except:
                pass  # Speech is optional
        
        return self.send_notification(title, message, sound=False)  # Don't double-speak


@dataclass
class PRAlert:
    pr_id: int
    repo_name: str
    title: str
    author: str
    url: str
    created_at: datetime
    first_seen: datetime
    last_reminder: Optional[datetime] = None


class AudioNotifier:
    """Handle audio notifications for PR reviews"""
    
    def __init__(self):
        """Initialize audio notifier with ElevenLabs if available"""
        self.tts = None
        try:
            from pr_notifier.pr_audio_monitor import ElevenLabsTTS
            self.tts = ElevenLabsTTS()
            logging.info("ElevenLabs TTS initialized with custom voice")
        except ImportError:
            logging.warning("ElevenLabs not available, using macOS say command")
    
    def send_audio_notification(self, message: str, voice: str = "Alex") -> bool:
        """Send audio notification using ElevenLabs or fallback to macOS say"""
        if self.tts:
            # Use ElevenLabs with custom voice
            try:
                return self.tts.speak(message)
            except Exception as e:
                logging.error(f"ElevenLabs failed: {e}, falling back to macOS say")
        
        # Fallback to macOS say command
        try:
            subprocess.run([
                "say", "-v", voice, message
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to send audio notification: {e}")
            return False
    
    def announce_new_pr(self, repo_name: str, title: str) -> bool:
        """Announce new PR creation"""
        # Clean up repo name and title for speech
        clean_repo = repo_name.replace("-", " ").replace("_", " ")
        clean_title = title.replace("-", " ").replace("_", " ")
        
        message = f"Pull request created for review in repository {clean_repo}. Title: {clean_title}. Please review and approve."
        return self.send_audio_notification(message)
    
    def announce_pr_reminder(self, repo_name: str, title: str) -> bool:
        """Announce PR review reminder"""
        # Clean up repo name and title for speech
        clean_repo = repo_name.replace("-", " ").replace("_", " ")
        clean_title = title.replace("-", " ").replace("_", " ")
        
        message = f"Reminder: Pull request in {clean_repo} is still waiting for review. Title: {clean_title}."
        return self.send_audio_notification(message)


class PRMonitor:
    """Monitor GitHub Pull Requests for automation-created PRs"""
    
    def __init__(self, config: MonitorConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.audio_notifier = AudioNotifier()
        self.tracked_prs: Dict[int, PRAlert] = {}  # pr_id -> PRAlert
        
    def _is_automation_pr(self, pr_data: Dict) -> bool:
        """Check if PR was created by automation"""
        author = pr_data.get('user', {}).get('login', '')
        title = pr_data.get('title', '')
        
        # Check if author matches automation patterns
        if any(auth_pattern in author for auth_pattern in self.config.pr_automation_authors):
            return True
        
        # Check if title matches automation patterns
        if any(pattern in title for pattern in self.config.pr_title_patterns):
            return True
        
        return False
    
    def _should_send_reminder(self, pr_alert: PRAlert) -> bool:
        """Check if reminder should be sent for this PR"""
        now = datetime.now()
        
        # If no reminder sent yet, check if enough time passed since first seen
        if pr_alert.last_reminder is None:
            time_since_first = (now - pr_alert.first_seen).total_seconds()
            return time_since_first >= self.config.pr_reminder_interval
        
        # Check if enough time passed since last reminder
        time_since_last = (now - pr_alert.last_reminder).total_seconds()
        return time_since_last >= self.config.pr_reminder_interval
    
    def check_open_prs(self) -> List[PRAlert]:
        """Check for open automation PRs and return alerts"""
        if not self.config.enable_pr_monitoring:
            return []
        
        try:
            # This would use GitHub MCP in real implementation
            # For now, let's prepare the structure
            self.logger.debug("🔍 Checking for open automation PRs...")
            
            # TODO: Implement GitHub MCP integration to search for PRs
            # Query would be something like: "is:pr is:open author:github-actions"
            
            # Placeholder for GitHub MCP call
            # prs = github_mcp.search_pull_requests(query="is:pr is:open author:github-actions")
            
            # For now, return empty list - will implement GitHub integration next
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Error checking PRs: {e}")
            return []
    
    def handle_pr_alerts(self, pr_alerts: List[PRAlert]) -> None:
        """Handle PR alerts with audio notifications"""
        now = datetime.now()
        
        for pr_alert in pr_alerts:
            pr_id = pr_alert.pr_id
            
            # Check if this is a new PR
            if pr_id not in self.tracked_prs:
                self.logger.info(f"🎯 New automation PR detected: {pr_alert.repo_name}#{pr_id}")
                
                # Send new PR notification
                self.audio_notifier.announce_new_pr(pr_alert.repo_name, pr_alert.title)
                
                # Track the PR
                self.tracked_prs[pr_id] = pr_alert
                
                self.logger.info(f"🔔 Audio notification sent for new PR: {pr_alert.title}")
                
            else:
                # Update existing PR tracking
                existing_pr = self.tracked_prs[pr_id]
                
                # Check if reminder should be sent
                if self._should_send_reminder(existing_pr):
                    self.logger.info(f"⏰ Sending reminder for PR: {pr_alert.repo_name}#{pr_id}")
                    
                    # Send reminder notification
                    self.audio_notifier.announce_pr_reminder(pr_alert.repo_name, pr_alert.title)
                    
                    # Update last reminder time
                    existing_pr.last_reminder = now
                    
                    self.logger.info(f"🔔 Audio reminder sent for PR: {pr_alert.title}")
    
    def cleanup_closed_prs(self) -> None:
        """Remove closed PRs from tracking (placeholder for now)"""
        # TODO: Implement GitHub API call to check PR status
        # For now, we'll rely on the monitoring cycle to manage this
        pass


class DLQMonitor:
    """Monitor AWS SQS Dead Letter Queues in FABIO-PROD sa-east-1"""
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.sqs_client = self._init_aws_client()
        self.notifier = MacNotifier()
        self.last_alerts: Dict[str, datetime] = {}
        self.account_id = self._get_account_id()
        
        # Auto-investigation tracking
        self.auto_investigations: Dict[str, datetime] = {}  # Track when auto-investigation was started
        self.investigation_processes: Dict[str, subprocess.Popen] = {}  # Track running investigations
        self.investigation_cooldown: int = 3600  # 1 hour cooldown between investigations
        
    def _setup_logging(self) -> logging.Logger:
        """Configure structured logging with queue name emphasis"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - [QUEUE: %(queue_name)s] - %(message)s'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'dlq_monitor_{self.config.aws_profile}_{self.config.region}.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _init_aws_client(self) -> boto3.client:
        """Initialize AWS SQS client with FABIO-PROD profile and sa-east-1 region"""
        try:
            session = boto3.Session(
                profile_name=self.config.aws_profile,
                region_name=self.config.region
            )
            
            client = session.client('sqs')
            
            # Test connection and log configuration
            response = client.list_queues(MaxResults=1)
            self.logger.info(f"✅ Connected to AWS SQS")
            self.logger.info(f"📋 Profile: {self.config.aws_profile}")
            self.logger.info(f"🌍 Region: {self.config.region}")
            
            return client
            
        except NoCredentialsError:
            self.logger.error(f"❌ AWS credentials not found for profile: {self.config.aws_profile}")
            raise
        except ClientError as e:
            self.logger.error(f"❌ AWS client initialization failed: {e}")
            raise
    
    def _get_account_id(self) -> str:
        """Get AWS account ID"""
        try:
            sts = boto3.Session(profile_name=self.config.aws_profile).client('sts', region_name=self.config.region)
            response = sts.get_caller_identity()
            account_id = response['Account']
            self.logger.info(f"🏢 Account ID: {account_id}")
            return account_id
        except Exception as e:
            self.logger.warning(f"Could not determine account ID: {e}")
            return "unknown"
    
    def _is_dlq(self, queue_name: str) -> bool:
        """Check if queue name matches DLQ patterns"""
        return any(pattern in queue_name.lower() for pattern in self.config.dlq_patterns)
    
    def discover_dlq_queues(self) -> List[Dict[str, str]]:
        """Discover all DLQ queues in FABIO-PROD sa-east-1"""
        try:
            paginator = self.sqs_client.get_paginator('list_queues')
            dlq_queues = []
            
            for page in paginator.paginate():
                if 'QueueUrls' in page:
                    for queue_url in page['QueueUrls']:
                        queue_name = queue_url.split('/')[-1]
                        
                        if self._is_dlq(queue_name):
                            dlq_queues.append({
                                'name': queue_name,
                                'url': queue_url
                            })
            
            if dlq_queues:
                self.logger.info(f"🔍 Discovered {len(dlq_queues)} DLQ queues in FABIO-PROD sa-east-1:")
                for queue in dlq_queues:
                    self.logger.info(f"   📋 {queue['name']}")
            else:
                self.logger.info("ℹ️  No DLQ queues found in FABIO-PROD sa-east-1")
            
            return dlq_queues
            
        except ClientError as e:
            self.logger.error(f"❌ Failed to discover DLQ queues: {e}")
            return []
    
    def get_queue_message_count(self, queue_url: str) -> int:
        """Get approximate number of messages in queue"""
        try:
            response = self.sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['ApproximateNumberOfMessages']
            )
            
            return int(response['Attributes'].get('ApproximateNumberOfMessages', 0))
            
        except ClientError as e:
            queue_name = queue_url.split('/')[-1]
            self.logger.error(f"❌ Failed to get message count for {queue_name}: {e}")
            return 0
    
    def check_dlq_messages(self) -> List[DLQAlert]:
        """Check all DLQs for messages and return alerts with queue names"""
        dlq_queues = self.discover_dlq_queues()
        alerts = []
        
        for queue in dlq_queues:
            message_count = self.get_queue_message_count(queue['url'])
            queue_name = queue['name']
            
            # Log every queue check with name
            if message_count > 0:
                self.logger.warning(f"⚠️  DLQ {queue_name} has {message_count} messages")
            else:
                self.logger.debug(f"✅ DLQ {queue_name} is empty")
            
            if message_count > 0:
                alert = DLQAlert(
                    queue_name=queue_name,
                    queue_url=queue['url'],
                    message_count=message_count,
                    timestamp=datetime.now(),
                    region=self.config.region,
                    account_id=self.account_id
                )
                alerts.append(alert)
                
                # Handle alert with prominent queue name
                self._handle_alert(alert)
        
        return alerts
    
    def _should_auto_investigate(self, queue_name: str) -> bool:
        """Check if auto-investigation should be triggered for this queue"""
        if queue_name not in self.config.auto_investigate_dlqs:
            return False
        
        # Check if investigation is already running
        if queue_name in self.investigation_processes:
            proc = self.investigation_processes[queue_name]
            if proc.poll() is None:  # Process is still running
                self.logger.info(f"🔍 Auto-investigation already running for {queue_name}")
                return False
            else:
                # Process finished, clean up
                del self.investigation_processes[queue_name]
        
        # Check cooldown period
        if queue_name in self.auto_investigations:
            last_investigation = self.auto_investigations[queue_name]
            time_since_last = datetime.now() - last_investigation
            if time_since_last.total_seconds() < self.investigation_cooldown:
                remaining = self.investigation_cooldown - time_since_last.total_seconds()
                self.logger.info(f"🕐 Auto-investigation cooldown for {queue_name}: {remaining/60:.1f} minutes remaining")
                return False
        
        return True
    
    def _execute_claude_investigation(self, queue_name: str, message_count: int = 0) -> None:
        """Execute Claude command for DLQ investigation in background thread"""
        def run_investigation():
            try:
                self.logger.info(f"🚀 Starting auto-investigation for {queue_name}")
                
                # Send notification about starting investigation
                self.notifier.send_notification(
                    f"🔍 AUTO-INVESTIGATION STARTED",
                    f"Queue: {queue_name}\nStarting Claude investigation...\nThis may take up to 30 minutes."
                )
                
                # Prepare Claude command with enhanced multi-agent capabilities
                claude_prompt = f"""🚨 CRITICAL DLQ INVESTIGATION REQUIRED: {queue_name}

📋 CONTEXT:
- AWS Profile: FABIO-PROD
- Region: sa-east-1
- Queue: {queue_name}
- Messages in DLQ: {message_count}

🎯 YOUR MISSION (USE CLAUDE CODE FOR ALL TASKS):

1. **MULTI-SUBAGENT INVESTIGATION**:
   - Deploy multiple subagents to investigate in parallel
   - Use ultrathink for deep analysis and root cause identification
   - Each subagent should focus on different aspects:
     * Subagent 1: Analyze DLQ messages and error patterns
     * Subagent 2: Check CloudWatch logs for related errors
     * Subagent 3: Review codebase for potential issues
     * Subagent 4: Identify configuration or deployment problems

2. **USE ALL MCP TOOLS**:
   - Use sequential-thinking MCP for step-by-step problem solving
   - Use filesystem MCP to analyze and fix code
   - Use GitHub MCP to check recent changes and create PRs
   - Use memory MCP to track investigation progress
   - Use any other relevant MCP tools available

3. **ULTRATHINK ANALYSIS**:
   - Apply ultrathink reasoning for complex problem solving
   - Consider multiple hypotheses for the root cause
   - Validate each hypothesis with evidence from logs and code
   - Choose the most likely solution based on evidence

4. **COMPREHENSIVE FIX**:
   - Identify ALL issues causing messages to go to DLQ
   - Fix the root cause in the codebase
   - Add proper error handling to prevent future occurrences
   - Include logging improvements for better debugging

5. **CODE CHANGES & DEPLOYMENT**:
   - Make necessary code changes using filesystem MCP
   - **COMMIT the code changes** with descriptive commit message
   - Create a Pull Request with detailed description of:
     * Root cause analysis
     * Changes made
     * Testing performed
     * Prevention measures

6. **DLQ CLEANUP**:
   - After fixes are committed, purge the DLQ messages
   - Verify the queue is clean
   - Document the incident resolution

⚡ IMPORTANT INSTRUCTIONS:
- Use CLAUDE CODE for all operations (not just responses)
- Deploy MULTIPLE SUBAGENTS working in parallel
- Use ULTRATHINK for deep reasoning
- Leverage ALL available MCP tools
- Be thorough and fix ALL issues, not just symptoms
- Create a comprehensive PR with full documentation
- This is PRODUCTION - be careful but thorough

🔄 Start the multi-agent investigation NOW!"""
                
                # Execute Claude command with proper quoting
                # Claude expects: claude -p "prompt"
                cmd = ['claude', '-p', claude_prompt]
                
                self.logger.info(f"🔍 Executing Claude investigation: {' '.join(cmd[:2])} [PROMPT_HIDDEN]")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.expanduser('~')  # Run from home directory
                )
                
                # Store the process for tracking
                self.investigation_processes[queue_name] = process
                
                # Wait for completion with timeout
                try:
                    stdout, stderr = process.communicate(timeout=self.config.claude_command_timeout)
                    
                    if process.returncode == 0:
                        self.logger.info(f"✅ Claude investigation completed successfully for {queue_name}")
                        
                        # Send success notification
                        self.notifier.send_notification(
                            f"✅ AUTO-INVESTIGATION COMPLETED",
                            f"Queue: {queue_name}\nClaude investigation finished successfully.\nCheck logs for details."
                        )
                        
                        # Log Claude output (truncated)
                        if stdout:
                            self.logger.info(f"📋 Claude investigation output (first 500 chars): {stdout[:500]}...")
                        
                    else:
                        self.logger.error(f"❌ Claude investigation failed for {queue_name} (exit code: {process.returncode})")
                        if stderr:
                            self.logger.error(f"📋 Claude error output: {stderr[:500]}...")
                        
                        # Send failure notification
                        self.notifier.send_notification(
                            f"❌ AUTO-INVESTIGATION FAILED",
                            f"Queue: {queue_name}\nClaude investigation failed.\nCheck logs for details."
                        )
                
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"⏰ Claude investigation timed out for {queue_name} after {self.config.claude_command_timeout}s")
                    process.kill()
                    
                    # Send timeout notification
                    self.notifier.send_notification(
                        f"⏰ AUTO-INVESTIGATION TIMEOUT",
                        f"Queue: {queue_name}\nClaude investigation timed out after {self.config.claude_command_timeout/60:.0f} minutes."
                    )
                    
                finally:
                    # Clean up process tracking
                    if queue_name in self.investigation_processes:
                        del self.investigation_processes[queue_name]
                
            except Exception as e:
                self.logger.error(f"❌ Auto-investigation error for {queue_name}: {e}")
                
                # Send error notification
                self.notifier.send_notification(
                    f"❌ AUTO-INVESTIGATION ERROR",
                    f"Queue: {queue_name}\nError: {str(e)[:100]}..."
                )
                
            finally:
                # Record investigation attempt
                self.auto_investigations[queue_name] = datetime.now()
                self.logger.info(f"🏁 Auto-investigation completed for {queue_name}")
        
        # Start investigation in background thread
        investigation_thread = threading.Thread(
            target=run_investigation,
            name=f"claude-investigation-{queue_name}",
            daemon=True
        )
        investigation_thread.start()
        
        self.logger.info(f"🔍 Started auto-investigation thread for {queue_name}")
    
    def _handle_alert(self, alert: DLQAlert) -> None:
        """Handle DLQ alert with prominent queue name display"""
        queue_name = alert.queue_name
        
        # Check if this is a new alert or if enough time has passed
        should_notify = (
            queue_name not in self.last_alerts or
            (datetime.now() - self.last_alerts[queue_name]).seconds > 300  # 5 min cooldown
        )
        
        if should_notify:
            # Send Mac notification with queue name prominently displayed
            self.notifier.send_critical_alert(
                queue_name, 
                alert.message_count, 
                alert.region
            )
            self.last_alerts[queue_name] = alert.timestamp
            
            # Log with extra emphasis on queue name
            self.logger.critical(
                f"🚨 CRITICAL DLQ ALERT 🚨"
            )
            self.logger.critical(
                f"📋 QUEUE NAME: {queue_name}"
            )
            self.logger.critical(
                f"📊 MESSAGE COUNT: {alert.message_count}"
            )
            self.logger.critical(
                f"🌍 REGION: {alert.region}"
            )
            self.logger.critical(
                f"🏢 ACCOUNT: {alert.account_id}"
            )
            self.logger.critical(
                f"🔗 QUEUE URL: {alert.queue_url}"
            )
            self.logger.critical(
                f"⏰ TIMESTAMP: {alert.timestamp.isoformat()}"
            )
            self.logger.critical("=" * 80)
            
            # Console output with queue name emphasis
            print(f"\n🚨 DLQ ALERT - QUEUE: {queue_name} 🚨")
            print(f"📊 Messages: {alert.message_count}")
            print(f"🌍 Region: {alert.region}")
            print(f"⏰ Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 50)
            
            # Check if auto-investigation should be triggered
            if self._should_auto_investigate(queue_name):
                self.logger.info(f"🎆 Triggering auto-investigation for {queue_name}")
                print(f"🔍 🤖 TRIGGERING CLAUDE AUTO-INVESTIGATION for {queue_name}")
                print(f"📊 Expected duration: up to {self.config.claude_command_timeout/60:.0f} minutes")
                print(f"🔔 You'll receive notifications when investigation completes")
                print("=" * 50)
                
                # Execute Claude investigation in background
                self._execute_claude_investigation(queue_name, alert.message_count)
            else:
                # Log why auto-investigation was not triggered
                if queue_name in self.config.auto_investigate_dlqs:
                    if queue_name in self.investigation_processes:
                        print(f"🔍 Claude investigation already running for {queue_name}")
                    elif queue_name in self.auto_investigations:
                        last_investigation = self.auto_investigations[queue_name]
                        time_since_last = datetime.now() - last_investigation
                        remaining = self.investigation_cooldown - time_since_last.total_seconds()
                        if remaining > 0:
                            print(f"🕐 Auto-investigation cooldown: {remaining/60:.1f} minutes remaining")
    
    def run_continuous_monitoring(self) -> None:
        """Run continuous monitoring loop for FABIO-PROD sa-east-1"""
        print(f"\n🚀 Starting DLQ monitoring")
        print(f"📋 AWS Profile: {self.config.aws_profile}")
        print(f"🌍 Region: {self.config.region}")
        print(f"⏱️  Check interval: {self.config.check_interval} seconds")
        print(f"🔔 Notifications: {'Enabled' if self.config.notification_sound else 'Disabled'}")
        print(f"📂 Log file: dlq_monitor_{self.config.aws_profile}_{self.config.region}.log")
        print("=" * 80)
        
        self.logger.info(f"🚀 Starting DLQ monitoring for profile: {self.config.aws_profile}")
        self.logger.info(f"🌍 Region: {self.config.region}")
        self.logger.info(f"⏱️  Check interval: {self.config.check_interval} seconds")
        
        try:
            cycle_count = 0
            while True:
                try:
                    cycle_count += 1
                    print(f"\n🔄 Monitoring cycle {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                    
                    alerts = self.check_dlq_messages()
                    
                    if alerts:
                        print(f"⚠️  Found {len(alerts)} DLQ(s) with messages:")
                        for alert in alerts:
                            print(f"   📋 {alert.queue_name}: {alert.message_count} messages")
                        self.logger.warning(f"Found {len(alerts)} DLQ(s) with messages")
                    else:
                        print("✅ All DLQs are empty")
                        self.logger.info("All DLQs are empty")
                    
                    print(f"⏳ Next check in {self.config.check_interval} seconds...")
                    time.sleep(self.config.check_interval)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Monitoring stopped by user")
                    self.logger.info("Monitoring stopped by user")
                    break
                except Exception as e:
                    print(f"❌ Error during monitoring cycle: {e}")
                    self.logger.error(f"Error during monitoring cycle: {e}")
                    time.sleep(self.config.check_interval)
                    
        except Exception as e:
            print(f"💥 Critical error in monitoring loop: {e}")
            self.logger.error(f"Critical error in monitoring loop: {e}")
            raise


def main():
    """Main entry point for FABIO-PROD monitoring"""
    print("🎯 AWS SQS DLQ Monitor - FABIO-PROD Edition")
    
    config = MonitorConfig(
        aws_profile="FABIO-PROD",
        region="sa-east-1",
        check_interval=30,
        notification_sound=True
    )
    
    try:
        monitor = DLQMonitor(config)
        monitor.run_continuous_monitoring()
    except Exception as e:
        print(f"\n💥 Failed to start monitoring: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check AWS credentials: aws configure list --profile FABIO-PROD")
        print("   2. Test AWS access: aws sqs list-queues --profile FABIO-PROD --region sa-east-1")
        print("   3. Verify profile exists: cat ~/.aws/credentials")


if __name__ == "__main__":
    main()
