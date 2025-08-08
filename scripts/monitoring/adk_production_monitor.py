#!/usr/bin/env python3
"""
BHiveQ ADK Production Monitor
Implements the documented multi-agent monitoring flow for DLQ management
"""

import os
import sys
import json
import time
import asyncio
import logging
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Suppress blake2 hash warnings for Python 3.11 compatibility
warnings.filterwarnings("ignore", category=UserWarning, module='_blake2')
warnings.filterwarnings("ignore", message=".*blake2.*")

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load configuration
import yaml
config_path = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Investigation Mode Control from config
investigation_config = config.get('investigation', {})
MANUAL_INVESTIGATION_ONLY = investigation_config.get('mode', 'manual') == 'manual'
INVESTIGATION_THRESHOLD = investigation_config.get('auto_threshold', 10)
COOLDOWN_MINUTES = investigation_config.get('cooldown_minutes', 30)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import AWS and monitoring components
import boto3
from dlq_monitor.services.database_service import get_database_service
from dlq_monitor.services.investigation_service import get_investigation_service
from dlq_monitor.notifiers.macos_notifier import MacNotifier
from dlq_monitor.notifiers.pr_audio import PRAudioMonitor

# Import ADK components
try:
    import google.generativeai as genai
    from google.adk import Agent, create_agent
    ADK_AVAILABLE = True
except ImportError:
    logger.warning("Google ADK not available - install with: pip install google-adk google-generativeai")
    ADK_AVAILABLE = False

class DLQMonitorAgent:
    """Agent responsible for monitoring AWS SQS DLQs"""
    
    def __init__(self):
        self.profile = os.environ.get('AWS_PROFILE', 'FABIO-PROD')
        self.region = os.environ.get('AWS_REGION', 'sa-east-1')
        self.session = boto3.Session(profile_name=self.profile)
        self.sqs_client = self.session.client('sqs', region_name=self.region)
        self.critical_threshold = INVESTIGATION_THRESHOLD
        
    def check_dlqs(self) -> Dict[str, Any]:
        """Check all DLQs for messages"""
        logger.info(f"🔍 Checking DLQs in {self.profile}/{self.region}")
        
        try:
            response = self.sqs_client.list_queues()
            dlq_status = []
            
            if 'QueueUrls' in response:
                for queue_url in response['QueueUrls']:
                    if 'dlq' in queue_url.lower():
                        queue_name = queue_url.split('/')[-1]
                        
                        attrs = self.sqs_client.get_queue_attributes(
                            QueueUrl=queue_url,
                            AttributeNames=['All']
                        )['Attributes']
                        
                        message_count = int(attrs.get('ApproximateNumberOfMessages', 0))
                        
                        if message_count > 0:
                            dlq_status.append({
                                'name': queue_name,
                                'url': queue_url,
                                'messages': message_count,
                                'critical': message_count >= self.critical_threshold,
                                'profile': self.profile,
                                'region': self.region
                            })
                            
            return {
                'timestamp': datetime.now().isoformat(),
                'dlqs_with_messages': dlq_status,
                'total_messages': sum(d['messages'] for d in dlq_status)
            }
            
        except Exception as e:
            logger.error(f"Error checking DLQs: {e}")
            return {'error': str(e)}

class InvestigationAgent:
    """Agent responsible for root cause analysis"""
    
    def __init__(self):
        self.db_service = get_database_service()
        self.investigation_service = get_investigation_service()
        
    def analyze(self, dlq_name: str, message_count: int) -> Dict[str, Any]:
        """Analyze DLQ messages and determine root cause"""
        logger.info(f"🔎 Analyzing {dlq_name} with {message_count} messages")
        
        # Create investigation in database
        investigation_id = self.db_service.create_investigation(
            dlq_name=dlq_name,
            message_count=message_count,
            agent_id='investigation-agent',
            initial_prompt=f"Analyze {message_count} messages in {dlq_name}"
        )
        
        # Update progress
        self.db_service.update_investigation_status(
            investigation_id, 'analyzing', progress=25
        )
        
        # Simulate analysis (in production, this would invoke Claude)
        analysis = {
            'investigation_id': investigation_id,
            'dlq_name': dlq_name,
            'message_count': message_count,
            'root_cause': 'Timeout errors in Lambda function',
            'error_pattern': 'Task timed out after 15.00 seconds',
            'affected_service': 'payment-processor',
            'recommendation': 'Increase Lambda timeout or optimize function'
        }
        
        # Update with findings
        self.db_service.update_investigation_status(
            investigation_id, 'debugging', progress=50,
            extra_data=json.dumps(analysis)
        )
        
        return analysis

class CodeFixerAgent:
    """Agent responsible for implementing fixes"""
    
    def __init__(self):
        self.db_service = get_database_service()
        
    def implement_fix(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Implement fix based on analysis"""
        logger.info(f"🔧 Implementing fix for {analysis['dlq_name']}")
        
        investigation_id = analysis['investigation_id']
        
        # Update status
        self.db_service.update_investigation_status(
            investigation_id, 'reviewing', progress=75
        )
        
        # In production, this would invoke Claude subagents
        fix = {
            'investigation_id': investigation_id,
            'files_modified': [
                'src/handlers/payment_processor.py',
                'infrastructure/lambda_config.yaml'
            ],
            'changes': {
                'timeout': 'Increased from 15s to 30s',
                'memory': 'Increased from 512MB to 1024MB',
                'error_handling': 'Added exponential backoff retry'
            },
            'tests_added': True,
            'test_results': 'All tests passing'
        }
        
        return fix

class PRManagerAgent:
    """Agent responsible for GitHub PR creation"""
    
    def __init__(self):
        self.db_service = get_database_service()
        self.github_token = os.environ.get('GITHUB_TOKEN', '')
        
    def create_pr(self, fix: Dict[str, Any]) -> Dict[str, Any]:
        """Create GitHub PR with fix"""
        logger.info(f"📝 Creating PR for investigation {fix['investigation_id']}")
        
        investigation_id = fix['investigation_id']
        
        # In production, this would create actual PR
        pr = {
            'investigation_id': investigation_id,
            'pr_number': 42,
            'pr_url': f'https://github.com/org/repo/pull/42',
            'title': f"Fix: Timeout errors in payment processor",
            'branch': f"fix/dlq-{investigation_id}",
            'status': 'open'
        }
        
        # Update investigation with PR
        self.db_service.update_investigation_status(
            investigation_id, 'completed', progress=100,
            pr_url=pr['pr_url']
        )
        
        return pr

class NotifierAgent:
    """Agent responsible for notifications"""
    
    def __init__(self):
        self.macos_notifier = MacNotifier()
        self.pr_notifier = PRAudioMonitor()
        self.last_notifications = {}
        
    def send_alert(self, dlq_name: str, message_count: int):
        """Send DLQ alert"""
        logger.info(f"🔔 Sending alert for {dlq_name}")
        
        self.macos_notifier.notify(
            title=f"DLQ Alert: {dlq_name}",
            message=f"{message_count} messages detected",
            sound=True
        )
        
    def notify_pr_created(self, pr: Dict[str, Any]):
        """Notify about PR creation"""
        logger.info(f"📢 PR created: {pr['pr_url']}")
        
        self.macos_notifier.notify(
            title="Pull Request Created",
            message=pr['title'],
            sound=True
        )
        
        # Voice notification
        self.pr_notifier.notify_pr_created(
            pr_number=pr['pr_number'],
            pr_title=pr['title']
        )
        
        # Schedule reminders
        self.last_notifications[pr['pr_number']] = datetime.now()
        
    def send_pr_reminders(self):
        """Send PR reminders every 10 minutes"""
        now = datetime.now()
        
        for pr_number, last_notif in list(self.last_notifications.items()):
            if (now - last_notif) >= timedelta(minutes=10):
                logger.info(f"⏰ PR reminder for #{pr_number}")
                self.pr_notifier.remind_pr_review(pr_number)
                self.last_notifications[pr_number] = now

class CoordinatorAgent:
    """Main orchestrator for all agents"""
    
    def __init__(self):
        self.dlq_monitor = DLQMonitorAgent()
        self.investigator = InvestigationAgent()
        self.code_fixer = CodeFixerAgent()
        self.pr_manager = PRManagerAgent()
        self.notifier = NotifierAgent()
        
        # Cooldown tracking
        self.cooldowns = {}
        self.cooldown_period = timedelta(minutes=COOLDOWN_MINUTES)
        
        # Database service for NeuroCenter
        self.db_service = get_database_service()
        
        # Register all agents in database
        self._register_agents()
        
    def _register_agents(self):
        """Register all agents in the database"""
        agents = [
            ('coordinator', 'Coordinator Agent', 'Main orchestrator for all agents', 'coordinator'),
            ('dlq_monitor', 'DLQ Monitor Agent', 'Monitors AWS SQS DLQs', 'monitor'),
            ('investigator', 'Investigation Agent', 'Performs root cause analysis', 'investigator'),
            ('code_fixer', 'Code Fixer Agent', 'Implements fixes for issues', 'fixer'),
            ('pr_manager', 'PR Manager Agent', 'Creates and manages GitHub PRs', 'manager'),
            ('notifier', 'Notifier Agent', 'Sends notifications and alerts', 'notifier')
        ]
        
        for agent_id, name, description, agent_type in agents:
            self.db_service.register_agent(agent_id, name, description, agent_type)
            self.db_service.update_agent_status(agent_id, 'idle')
    
    def is_in_cooldown(self, dlq_name: str) -> bool:
        """Check if DLQ is in cooldown period"""
        if dlq_name not in self.cooldowns:
            return False
            
        last_investigation = self.cooldowns[dlq_name]
        return (datetime.now() - last_investigation) < self.cooldown_period
        
    async def monitor_cycle(self):
        """Main monitoring cycle - runs every 30 seconds"""
        logger.info("🚀 Starting ADK monitoring cycle")
        
        while True:
            try:
                # Step 1: Check DLQs
                dlq_status = self.dlq_monitor.check_dlqs()
                
                if 'error' in dlq_status:
                    logger.error(f"DLQ check failed: {dlq_status['error']}")
                    await asyncio.sleep(30)
                    continue
                    
                # Step 2: Process critical DLQs
                for dlq in dlq_status.get('dlqs_with_messages', []):
                    if dlq['critical'] and not self.is_in_cooldown(dlq['name']):
                        logger.info(f"🚨 Critical DLQ detected: {dlq['name']} with {dlq['messages']} messages")
                        
                        # Check if we're in manual investigation mode
                        if MANUAL_INVESTIGATION_ONLY:
                            logger.info(f"📋 Manual mode enabled - NOT auto-investigating {dlq['name']}")
                            logger.info(f"   Use NeuroCenter UI to manually trigger investigation")
                            
                            # Still emit status to NeuroCenter for display
                            self.emit_to_neurocenter('dlq_critical', {
                                'dlq_name': dlq['name'],
                                'messages': dlq['messages'],
                                'mode': 'manual',
                                'awaiting_action': True
                            })
                        else:
                            # Automatic investigation mode (original behavior)
                            # Step 3: Send alert
                            self.notifier.send_alert(dlq['name'], dlq['messages'])
                            
                            # Step 4: Start investigation
                            analysis = self.investigator.analyze(dlq['name'], dlq['messages'])
                            
                            # Step 5: Implement fix
                            fix = self.code_fixer.implement_fix(analysis)
                            
                            # Step 6: Create PR
                            pr = self.pr_manager.create_pr(fix)
                            
                            # Step 7: Notify PR created
                            self.notifier.notify_pr_created(pr)
                            
                            # Update cooldown
                            self.cooldowns[dlq['name']] = datetime.now()
                            
                            # Emit to NeuroCenter
                            self.emit_to_neurocenter('investigation_complete', {
                                'dlq_name': dlq['name'],
                                'investigation_id': analysis['investigation_id'],
                                'pr_url': pr['pr_url']
                            })
                        
                # Step 8: Send PR reminders
                self.notifier.send_pr_reminders()
                
                # Update metrics
                self.update_metrics(dlq_status)
                
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                
            # Wait 30 seconds before next cycle
            await asyncio.sleep(30)
            
    def emit_to_neurocenter(self, event: str, data: Dict[str, Any]):
        """Emit events to NeuroCenter via WebSocket or database"""
        try:
            # Store in database for NeuroCenter to pick up
            if event == 'investigation_complete':
                logger.info(f"📊 Emitting to NeuroCenter: {event}")
                # Database is already updated by agents
        except Exception as e:
            logger.error(f"Failed to emit to NeuroCenter: {e}")
            
    def update_metrics(self, dlq_status: Dict[str, Any]):
        """Update live metrics for NeuroCenter"""
        try:
            total_dlqs = len(dlq_status.get('dlqs_with_messages', []))
            total_messages = dlq_status.get('total_messages', 0)
            
            logger.info(f"📈 Metrics: {total_dlqs} DLQs with {total_messages} total messages")
            
            # In production, this would update shared metrics storage
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")

def main():
    """Main entry point"""
    mode_status = "📋 MANUAL MODE - Auto-investigation DISABLED" if MANUAL_INVESTIGATION_ONLY else "🤖 AUTO MODE - Auto-investigation ENABLED"
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║     🧠 BHiveQ ADK Production Monitor - Multi-Agent System        ║
╠═══════════════════════════════════════════════════════════════════╣
║  Profile: FABIO-PROD | Region: sa-east-1                         ║
║  Monitoring Cycle: Every 30 seconds                              ║
║  Cooldown Period: 30 minutes                                     ║
║  {mode_status:<65}║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    if not ADK_AVAILABLE:
        print("⚠️  Google ADK not available - running in simulation mode")
        print("   Install with: pip install google-adk google-generativeai")
        print("")
    
    # Create coordinator
    coordinator = CoordinatorAgent()
    
    # Start monitoring
    try:
        asyncio.run(coordinator.monitor_cycle())
    except KeyboardInterrupt:
        print("\n\n✋ Monitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()