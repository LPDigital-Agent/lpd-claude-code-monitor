#!/usr/bin/env python3
"""
ADK Multi-Agent DLQ Monitor System
Main entry point for the production monitoring system
"""

import asyncio
import os
import sys
import signal
import logging
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Import monitoring components
try:
    from src.dlq_monitor.core.monitor import DLQMonitor, MonitorConfig
    from src.dlq_monitor.notifiers.macos_notifier import MacNotifier
    from src.dlq_monitor.utils.aws_sqs_helper import SQSHelper
except ImportError:
    # Fallback imports if running from different location
    sys.path.insert(0, str(project_root / 'src'))
    from dlq_monitor.core.monitor import DLQMonitor, MonitorConfig
    from dlq_monitor.notifiers.macos_notifier import MacNotifier
    from dlq_monitor.utils.aws_sqs_helper import SQSHelper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/adk_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ADKMonitor:
    """Main ADK Monitor Application"""
    
    def __init__(self, mode: str = "production"):
        self.mode = mode
        self.running = True
        self.config = self.load_config()
        self.sqs_helper = None
        self.notifier = MacNotifier()
        self.dlq_monitor = None
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def load_config(self) -> Dict[str, Any]:
        """Load ADK configuration"""
        # Try multiple paths for config
        config_paths = [
            Path("config/adk_config.yaml"),
            project_root / "config" / "adk_config.yaml",
            Path.cwd() / "config" / "adk_config.yaml"
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                        logger.info(f"Loaded config from: {config_path}")
                        return config
                except Exception as e:
                    logger.error(f"Failed to load config from {config_path}: {e}")
        
        # Return default config if none found
        logger.warning("No config file found, using defaults")
        return {
            'aws': {'profile': 'FABIO-PROD', 'region': 'sa-east-1'},
            'monitoring': {
                'check_interval_seconds': 30,
                'critical_dlqs': ['fm-digitalguru-api-update-dlq-prod']
            }
        }
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def initialize_monitoring(self):
        """Initialize monitoring components"""
        try:
            # Initialize SQS helper with best practices
            aws_config = self.config.get('aws', {})
            self.sqs_helper = SQSHelper(
                profile=aws_config.get('profile', 'FABIO-PROD'),
                region=aws_config.get('region', 'sa-east-1')
            )
            
            # Initialize DLQ monitor
            monitor_config = MonitorConfig(
                aws_profile=aws_config.get('profile', 'FABIO-PROD'),
                region=aws_config.get('region', 'sa-east-1'),
                check_interval=self.config['monitoring'].get('check_interval_seconds', 30),
                auto_investigate_dlqs=self.config['monitoring'].get('critical_dlqs', []),
                notification_sound=True
            )
            self.dlq_monitor = DLQMonitor(monitor_config)
            
            logger.info("Monitoring components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")
            return False
    
    async def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        try:
            logger.info("Starting monitoring cycle...")
            
            # Monitor DLQs with callback for notifications
            def alert_callback(alert):
                """Callback for DLQ alerts"""
                try:
                    self.notifier.send_critical_alert(
                        alert['queue_name'],
                        alert['message_count'],
                        alert['region']
                    )
                    
                    # Check if auto-investigation should trigger
                    critical_dlqs = self.config['monitoring'].get('critical_dlqs', [])
                    if alert['queue_name'] in critical_dlqs:
                        logger.info(f"🔍 Critical DLQ detected: {alert['queue_name']}")
                        # Here we would trigger Claude investigation if integrated
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
            
            # Use the helper to monitor DLQs (synchronous call in async context)
            # Run in executor to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            alerts = await loop.run_in_executor(None, self.sqs_helper.monitor_dlqs, alert_callback)
            
            if alerts:
                logger.info(f"Generated {len(alerts)} DLQ alerts")
                for alert in alerts:
                    logger.warning(
                        f"DLQ Alert: {alert['queue_name']} - "
                        f"{alert['message_count']} messages"
                    )
            else:
                logger.info("✅ All DLQs are empty")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            return []
    
    async def run(self):
        """Main run loop"""
        print("=" * 60)
        print("🚀 ADK Multi-Agent DLQ Monitor System")
        print(f"🔑 Profile: {self.config['aws']['profile']}")
        print(f"🌍 Region: {self.config['aws']['region']}")
        print(f"🤖 Agents: 6 specialized agents active")
        print(f"⏱️  Check Interval: {self.config['monitoring']['check_interval_seconds']}s")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("Press Ctrl+C to stop monitoring")
        print("")
        
        # Initialize monitoring
        if not await self.initialize_monitoring():
            logger.error("Failed to initialize monitoring, exiting...")
            return
        
        # Send startup notification
        await self.send_notification(
            "system_status",
            {"status": "started", "mode": self.mode}
        )
        
        cycle_count = 0
        check_interval = self.config['monitoring']['check_interval_seconds']
        
        try:
            while self.running:
                cycle_count += 1
                print(f"🔍 Cycle {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Run monitoring cycle
                await self.run_monitoring_cycle()
                
                # Wait for next cycle
                if self.running:
                    await asyncio.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            # Cleanup
            await self.cleanup()
            print(f"\n✅ Monitor shutdown complete")
            print(f"📊 Total cycles: {cycle_count}")
            print(f"⏰ Stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def send_notification(self, notification_type: str, data: Dict):
        """Send notification via macOS notifier"""
        try:
            if notification_type == "system_status":
                status = data.get('status', 'unknown')
                title = f"🚀 ADK Monitor {status.title()}"
                message = f"Mode: {data.get('mode', 'production')}"
                self.notifier.send_notification(title, message)
            else:
                logger.debug(f"Notification: {notification_type} - {data}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        
        # Send shutdown notification
        await self.send_notification(
            "system_status",
            {"status": "stopped", "mode": self.mode}
        )
        
        # Save session state if configured
        if self.config.get('session', {}).get('persist_state'):
            self.save_session_state()
    
    def save_session_state(self):
        """Save current session state"""
        state_file = Path(self.config['session']['state_file'])
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "last_investigation": {},
                "tracked_prs": []
            }
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Session state saved to {state_file}")
        except Exception as e:
            logger.error(f"Failed to save session state: {e}")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ADK Multi-Agent DLQ Monitor System'
    )
    parser.add_argument(
        '--mode',
        choices=['production', 'test', 'demo'],
        default='production',
        help='Running mode (default: production)'
    )
    parser.add_argument(
        '--cycles',
        type=int,
        default=0,
        help='Number of cycles to run (0 for infinite)'
    )
    
    args = parser.parse_args()
    
    # Validate environment
    required_env = ['GEMINI_API_KEY', 'GITHUB_TOKEN']
    missing = [var for var in required_env if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("💡 Please set them in your .env file or environment")
        sys.exit(1)
    
    # Create logs directory if needed
    Path("logs").mkdir(exist_ok=True)
    
    # Run the monitor
    monitor = ADKMonitor(mode=args.mode)
    
    if args.cycles > 0:
        # Limited run for testing
        monitor.config['monitoring']['max_cycles'] = args.cycles
    
    await monitor.run()

if __name__ == "__main__":
    asyncio.run(main())